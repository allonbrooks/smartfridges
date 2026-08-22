from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, FamilyGroup, Member
from .serializers import (
    UserSerializer, FamilyGroupSerializer, MemberSerializer, JoinFamilySerializer
)


@api_view(['POST'])
def login(request):
    """微信登录/注册"""
    user = request.wx_user
    if not user:
        return Response({'error': '无法获取用户身份', 'success': False}, status=401)
    serializer = UserSerializer(user)
    return Response({'data': serializer.data, 'success': True})


@api_view(['POST'])
def create_family(request):
    """创建家庭组"""
    user = request.wx_user
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    serializer = FamilyGroupSerializer(
        data=request.data, context={'request': request}
    )
    serializer.is_valid(raise_exception=True)
    family = serializer.save()
    return Response({'data': FamilyGroupSerializer(family).data, 'success': True}, status=201)


@api_view(['POST'])
def join_family(request):
    """通过邀请码加入家庭"""
    user = request.wx_user
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    serializer = JoinFamilySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    family = get_object_or_404(
        FamilyGroup, invite_code=serializer.validated_data['invite_code']
    )
    if Member.objects.filter(user=user, family=family).exists():
        return Response({'error': '已在家庭中', 'success': False}, status=400)
    Member.objects.create(user=user, family=family)
    user.current_family = family
    user.save(update_fields=['current_family'])
    return Response({'data': FamilyGroupSerializer(family).data, 'success': True})


@api_view(['GET'])
def current_family(request):
    """获取当前家庭信息"""
    family = request.wx_family
    if not family:
        return Response({'error': '未加入任何家庭', 'success': False}, status=404)
    return Response({'data': FamilyGroupSerializer(family).data, 'success': True})


@api_view(['GET'])
def family_members(request, family_id):
    """成员列表"""
    family = get_object_or_404(FamilyGroup, id=family_id)
    members = Member.objects.filter(family=family).select_related('user')
    serializer = MemberSerializer(members, many=True)
    return Response({'data': serializer.data, 'success': True})


@api_view(['DELETE'])
def remove_member(request, family_id, user_id):
    """移除成员（仅管理员）"""
    user = request.wx_user
    if not user:
        return Response({'error': '未登录', 'success': False}, status=401)
    member = get_object_or_404(Member, user=user, family_id=family_id)
    if member.role != Member.Role.ADMIN:
        return Response({'error': '无权限', 'success': False}, status=403)
    target = get_object_or_404(Member, family_id=family_id, user_id=user_id)
    target.delete()
    return Response({'success': True})