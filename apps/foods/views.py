from datetime import date, timedelta
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.users.models import Member
from .models import FoodItem, StorageSpace, OperationLog
from .serializers import (
    FoodItemSerializer, FoodItemCreateSerializer, StorageSpaceSerializer,
    ConsumeSerializer, OperationLogSerializer,
)
from .services.voice_parser import parse_voice_text
from .services.barcode_service import lookup_barcode


def _log_operation(user, family, action, item, detail=''):
    """记录操作日志"""
    OperationLog.objects.create(
        family=family, user=user, action=action,
        item=item, item_name=item.name if item else '',
        detail=detail
    )


# --- 空间管理 ---

@api_view(['GET'])
def list_spaces(request):
    """当前家庭的所有空间"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    spaces = StorageSpace.objects.filter(family=family)
    serializer = StorageSpaceSerializer(spaces, many=True)
    return Response({'data': serializer.data, 'success': True})


@api_view(['POST'])
def create_space(request):
    """新建空间"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    serializer = StorageSpaceSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(family=family)
    return Response({'data': serializer.data, 'success': True}, status=201)


@api_view(['GET', 'PUT', 'DELETE'])
def space_detail(request, space_id):
    """查看/编辑/删除空间"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    space = get_object_or_404(StorageSpace, id=space_id, family=family)
    if request.method == 'GET':
        items = FoodItem.objects.filter(
            family=family, storage_space=space, is_consumed=False
        ).select_related('storage_space', 'added_by').order_by('expiry_date')
        space_serializer = StorageSpaceSerializer(space)
        item_serializer = FoodItemSerializer(items, many=True)
        return Response({
            'data': {
                'space': space_serializer.data,
                'items': item_serializer.data,
            },
            'success': True,
        })
    if request.method == 'DELETE':
        # 检查是否有物品
        if space.items.exists():
            return Response({'error': '该空间还有物品，请先移走', 'success': False}, status=400)
        space.delete()
        return Response({'success': True})
    # PUT
    serializer = StorageSpaceSerializer(space, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({'data': serializer.data, 'success': True})


# --- 物品管理 ---

@api_view(['GET'])
def item_overview(request):
    """红黄绿排序列表"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    items = FoodItem.objects.filter(
        family=family, is_consumed=False
    ).select_related('storage_space', 'added_by')

    # 计算状态并排序
    today = date.today()
    red, yellow, green = [], [], []
    for item in items:
        remaining = (item.expiry_date - today).days
        if remaining < 0:
            red.append(item)
        elif remaining <= 3:
            yellow.append(item)
        else:
            green.append(item)

    # 同色按到期日升序
    red.sort(key=lambda x: x.expiry_date)
    yellow.sort(key=lambda x: x.expiry_date)
    green.sort(key=lambda x: x.expiry_date)

    ordered = red + yellow + green
    serializer = FoodItemSerializer(ordered, many=True)
    return Response({
        'data': serializer.data,
        'counts': {'red': len(red), 'yellow': len(yellow), 'green': len(green)},
        'success': True
    })


@api_view(['GET'])
def list_items(request):
    """物品列表（支持筛选）"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    items = FoodItem.objects.filter(family=family).select_related('storage_space', 'added_by')
    # 筛选
    space_id = request.query_params.get('space_id')
    if space_id:
        items = items.filter(storage_space_id=space_id)
    category = request.query_params.get('category')
    if category:
        items = items.filter(category=category)
    consumed = request.query_params.get('consumed')
    if consumed == '1':
        items = items.filter(is_consumed=True)
    elif consumed != '1':
        items = items.filter(is_consumed=False)
    items = items.order_by('-created_at')
    from common.pagination import StandardPagination
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(items, request)
    serializer = FoodItemSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
def item_detail(request, item_id):
    """物品详情"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    item = get_object_or_404(FoodItem, id=item_id, family=family)
    serializer = FoodItemSerializer(item)
    return Response({'data': serializer.data, 'success': True})


@api_view(['POST'])
def create_item(request):
    """创建单个物品（手动录入/语音确认后使用）"""
    user = request.wx_user
    family = request.wx_family
    if not user or not family:
        return Response({'error': '未登录或未加入家庭', 'success': False}, status=401)
    serializer = FoodItemCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    item = serializer.save(family=family, added_by=user)
    _log_operation(user, family, OperationLog.Action.ADD, item, f'新增了 {item.name} x{item.quantity}{item.unit}')
    return Response({'data': FoodItemSerializer(item).data, 'success': True}, status=201)


@api_view(['POST'])
def create_items_batch(request):
    """批量创建物品（语音确认后使用）"""
    user = request.wx_user
    family = request.wx_family
    if not user or not family:
        return Response({'error': '未登录或未加入家庭', 'success': False}, status=401)
    items_data = request.data.get('items', [])
    if not items_data:
        return Response({'error': '物品列表为空', 'success': False}, status=400)
    space_id = request.data.get('storage_space_id')
    created = []
    for item_data in items_data:
        if space_id:
            item_data['storage_space_id'] = space_id
        serializer = FoodItemCreateSerializer(data=item_data)
        serializer.is_valid(raise_exception=True)
        item = serializer.save(family=family, added_by=user)
        _log_operation(user, family, OperationLog.Action.ADD, item, f'批量新增了 {item.name}')
        created.append(FoodItemSerializer(item).data)
    return Response({'data': created, 'success': True}, status=201)


@api_view(['POST'])
def barcode_entry(request):
    """条码录入"""
    user = request.wx_user
    family = request.wx_family
    if not user or not family:
        return Response({'error': '未登录或未加入家庭', 'success': False}, status=401)
    barcode = request.data.get('barcode', '')
    if not barcode:
        return Response({'error': '条码不能为空', 'success': False}, status=400)
    info = lookup_barcode(barcode)
    if info['found']:
        expiry_date = date.today() + timedelta(days=info['default_expiry_days'])
        item = FoodItem.objects.create(
            family=family, name=info['name'], category=info['category'],
            barcode=barcode, icon=info['icon'], quantity=1, unit='个',
            expiry_date=expiry_date, days_to_expire=info['default_expiry_days'],
            added_by=user,
        )
        _log_operation(user, family, OperationLog.Action.ADD, item, f'扫码新增了 {item.name}')
        return Response({'data': FoodItemSerializer(item).data, 'success': True}, status=201)
    return Response({'found': False, 'success': True})


@api_view(['POST'])
def voice_entry(request):
    """语音录入（解析仅返回，不保存）"""
    raw_text = request.data.get('raw_text', '')
    if not raw_text:
        return Response({'error': '语音文字不能为空', 'success': False}, status=400)
    result = parse_voice_text(raw_text)
    return Response({'data': result, 'success': True})


@api_view(['PATCH'])
def update_item(request, item_id):
    """编辑物品"""
    user = request.wx_user
    family = request.wx_family
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    item = get_object_or_404(FoodItem, id=item_id, family=family)
    serializer = FoodItemCreateSerializer(item, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    _log_operation(user, item.family, OperationLog.Action.MODIFY, item, f'修改了 {item.name}')
    return Response({'data': FoodItemSerializer(item).data, 'success': True})


@api_view(['PATCH'])
def consume_item(request, item_id):
    """消耗物品（减数量）"""
    user = request.wx_user
    family = request.wx_family
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    item = get_object_or_404(FoodItem, id=item_id, family=family)
    serializer = ConsumeSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    qty = serializer.validated_data['quantity']
    if item.quantity < qty:
        return Response({'error': f'剩余数量不足（当前 {item.quantity}）', 'success': False}, status=400)
    item.quantity -= qty
    if item.quantity == 0:
        item.is_consumed = True
        item.consumed_at = timezone.now()
    item.save()
    _log_operation(user, item.family, OperationLog.Action.CONSUME, item, f'消耗了 {qty}{item.unit}{item.name}')
    return Response({'data': FoodItemSerializer(item).data, 'success': True})


@api_view(['PATCH'])
def restore_item(request, item_id):
    """恢复已消耗物品"""
    user = request.wx_user
    family = request.wx_family
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    item = get_object_or_404(FoodItem, id=item_id, family=family)
    if not item.is_consumed:
        return Response({'error': '物品未消耗', 'success': False}, status=400)
    item.is_consumed = False
    item.consumed_at = None
    item.quantity = 1
    item.save()
    _log_operation(user, item.family, OperationLog.Action.MODIFY, item, f'恢复了 {item.name}')
    return Response({'data': FoodItemSerializer(item).data, 'success': True})


@api_view(['DELETE'])
def delete_item(request, item_id):
    """删除物品"""
    user = request.wx_user
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    item = get_object_or_404(FoodItem, id=item_id)
    # 检查权限：只有管理员或物品录入人可删除
    from apps.users.models import Member
    try:
        member = Member.objects.get(user=user, family=item.family)
    except Member.DoesNotExist:
        return Response({'error': '无权操作', 'success': False}, status=403)
    if member.role != Member.Role.ADMIN and item.added_by != user:
        return Response({'error': '无权限', 'success': False}, status=403)
    _log_operation(user, item.family, OperationLog.Action.DELETE, item, f'删除了 {item.name}')
    item.delete()
    return Response({'success': True})


# --- 操作日志 ---

@api_view(['GET'])
def list_logs(request):
    """家庭操作日志"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    logs = OperationLog.objects.filter(family=family).select_related('user')
    from common.pagination import StandardPagination
    paginator = StandardPagination()
    result_page = paginator.paginate_queryset(logs, request)
    serializer = OperationLogSerializer(result_page, many=True)
    return paginator.get_paginated_response(serializer.data)