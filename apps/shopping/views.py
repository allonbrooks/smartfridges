# apps/shopping/views.py
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import ShoppingList
from .serializers import ShoppingListSerializer, MarkPurchasedSerializer


@api_view(['GET'])
def list_shopping(request):
    """购物清单"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    items = ShoppingList.objects.filter(family=family)
    purchased = request.query_params.get('purchased')
    if purchased == '1':
        items = items.filter(is_purchased=True)
    elif purchased == '0':
        items = items.filter(is_purchased=False)
    items = items.order_by('is_purchased', '-created_at')
    serializer = ShoppingListSerializer(items, many=True)
    return Response({'data': serializer.data, 'success': True})


@api_view(['POST'])
def add_shopping_item(request):
    """手动添加购物清单项"""
    user = request.wx_user
    family = request.wx_family
    if not user or not family:
        return Response({'error': '未登录或未加入家庭', 'success': False}, status=401)
    serializer = ShoppingListSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save(family=family, created_by=user)
    return Response({'data': serializer.data, 'success': True}, status=201)


@api_view(['PATCH'])
def mark_purchased(request, item_id):
    """标记已购买/未购买"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入家庭', 'success': False}, status=404)
    item = get_object_or_404(ShoppingList, id=item_id, family=family)
    serializer = MarkPurchasedSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    item.is_purchased = serializer.validated_data['is_purchased']
    if item.is_purchased:
        item.purchased_at = timezone.now()
    else:
        item.purchased_at = None
    item.save()
    return Response({'data': ShoppingListSerializer(item).data, 'success': True})