import pytest
from django.urls import reverse
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestUserAPI:
    def test_login_without_openid_returns_401(self):
        """没有 X-WX-OPENID 头时返回 401"""
        client = APIClient()
        resp = client.post('/api/users/login')
        assert resp.status_code == 401

    def test_login_creates_user(self):
        """首次登录自动创建用户"""
        client = APIClient()
        resp = client.post('/api/users/login', HTTP_X_WX_OPENID='test_openid_1')
        assert resp.status_code == 200
        assert resp.json()['success'] is True
        assert resp.json()['data']['openid'] == 'test_openid_1'

    def test_login_returns_existing_user(self):
        """重复登录返回已有用户"""
        from apps.users.models import User
        User.objects.create(openid='existing_user')
        client = APIClient()
        resp = client.post('/api/users/login', HTTP_X_WX_OPENID='existing_user')
        assert resp.status_code == 200
        assert resp.json()['data']['openid'] == 'existing_user'


@pytest.mark.django_db
class TestFamilyAPI:
    def test_create_family(self):
        """创建家庭组"""
        client = APIClient()
        # 先登录
        client.post('/api/users/login', HTTP_X_WX_OPENID='family_owner')
        resp = client.post('/api/families', {'name': '我的家'}, HTTP_X_WX_OPENID='family_owner')
        assert resp.status_code == 201
        data = resp.json()['data']
        assert data['name'] == '我的家'
        assert len(data['invite_code']) == 6
        assert data['member_count'] == 1

    def test_join_family(self):
        """通过邀请码加入家庭"""
        from apps.users.models import FamilyGroup, User
        owner = User.objects.create(openid='owner')
        family = FamilyGroup.objects.create(name='测试家庭', invite_code='JOIN01', created_by=owner)
        from apps.users.models import Member
        Member.objects.create(user=owner, family=family, role='admin')

        client = APIClient()
        client.post('/api/users/login', HTTP_X_WX_OPENID='new_member')
        resp = client.post('/api/families/join', {'invite_code': 'JOIN01'}, HTTP_X_WX_OPENID='new_member')
        assert resp.status_code == 200
        assert resp.json()['data']['name'] == '测试家庭'

    def test_join_family_invalid_code(self):
        """无效邀请码返回 404"""
        client = APIClient()
        client.post('/api/users/login', HTTP_X_WX_OPENID='test_user')
        resp = client.post('/api/families/join', {'invite_code': 'INVALID'}, HTTP_X_WX_OPENID='test_user')
        assert resp.status_code == 404