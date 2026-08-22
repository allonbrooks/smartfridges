import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from apps.users.models import User, FamilyGroup, Member
from apps.foods.models import FoodItem, StorageSpace, OperationLog


@pytest.fixture
def setup_family():
    """创建测试用户和家庭"""
    client = APIClient()
    client.post('/api/users/login', HTTP_X_WX_OPENID='test_owner')
    resp = client.post('/api/families', {'name': '测试家庭'}, HTTP_X_WX_OPENID='test_owner')
    family_id = resp.json()['data']['id']
    return client, 'test_owner', family_id


@pytest.mark.django_db
class TestItemAPI:
    def test_create_item(self, setup_family):
        client, openid, family_id = setup_family
        resp = client.post('/api/items/create', {
            'name': '牛奶', 'category': 'dairy', 'quantity': 2, 'unit': '盒',
            'expiry_date': str(date.today() + timedelta(days=7)),
            'days_to_expire': 7,
        }, HTTP_X_WX_OPENID=openid)
        assert resp.status_code == 201
        assert resp.json()['data']['name'] == '牛奶'

    def test_consume_item(self, setup_family):
        client, openid, family_id = setup_family
        # 先创建
        client.post('/api/items/create', {
            'name': '鸡蛋', 'quantity': 3, 'unit': '个',
            'expiry_date': str(date.today() + timedelta(days=10)),
            'days_to_expire': 10,
        }, HTTP_X_WX_OPENID=openid)
        item_id = FoodItem.objects.first().id
        # 消耗 1 个
        resp = client.patch(
            f'/api/items/{item_id}/consume',
            {'quantity': 1},
            HTTP_X_WX_OPENID=openid,
            content_type='application/json'
        )
        assert resp.status_code == 200
        assert FoodItem.objects.get(id=item_id).quantity == 2

    def test_consume_all_makes_consumed(self, setup_family):
        client, openid, family_id = setup_family
        client.post('/api/items/create', {
            'name': '可乐', 'quantity': 1, 'unit': '瓶',
            'expiry_date': str(date.today() + timedelta(days=30)),
            'days_to_expire': 30,
        }, HTTP_X_WX_OPENID=openid)
        item_id = FoodItem.objects.first().id
        resp = client.patch(
            f'/api/items/{item_id}/consume',
            {'quantity': 1},
            HTTP_X_WX_OPENID=openid,
            content_type='application/json'
        )
        assert resp.status_code == 200
        item = FoodItem.objects.get(id=item_id)
        assert item.is_consumed
        assert item.consumed_at is not None

    def test_restore_item(self, setup_family):
        client, openid, family_id = setup_family
        client.post('/api/items/create', {
            'name': '面包', 'quantity': 1, 'unit': '个',
            'expiry_date': str(date.today() + timedelta(days=5)),
            'days_to_expire': 5,
        }, HTTP_X_WX_OPENID=openid)
        item_id = FoodItem.objects.first().id
        client.patch(f'/api/items/{item_id}/consume', {'quantity': 1}, HTTP_X_WX_OPENID=openid, content_type='application/json')
        resp = client.patch(f'/api/items/{item_id}/restore', HTTP_X_WX_OPENID=openid, content_type='application/json')
        assert resp.status_code == 200
        item = FoodItem.objects.get(id=item_id)
        assert not item.is_consumed
        assert item.quantity == 1

    def test_overview_red_yellow_green(self, setup_family):
        client, openid, family_id = setup_family
        # 创建已过期物品
        client.post('/api/items/create', {
            'name': '过期牛奶', 'quantity': 1, 'unit': '盒',
            'expiry_date': str(date.today() - timedelta(days=1)),
            'days_to_expire': 5,
        }, HTTP_X_WX_OPENID=openid)
        # 创建即将过期物品
        client.post('/api/items/create', {
            'name': '快过期鸡蛋', 'quantity': 1, 'unit': '个',
            'expiry_date': str(date.today() + timedelta(days=2)),
            'days_to_expire': 7,
        }, HTTP_X_WX_OPENID=openid)
        # 创建正常物品
        client.post('/api/items/create', {
            'name': '新鲜水果', 'quantity': 1, 'unit': '个',
            'expiry_date': str(date.today() + timedelta(days=10)),
            'days_to_expire': 10,
        }, HTTP_X_WX_OPENID=openid)
        resp = client.get('/api/items/overview', HTTP_X_WX_OPENID=openid)
        assert resp.status_code == 200
        counts = resp.json()['counts']
        assert counts['red'] == 1
        assert counts['yellow'] == 1
        assert counts['green'] == 1

    def test_voice_entry_returns_parsed(self, setup_family):
        client, openid, family_id = setup_family
        resp = client.post('/api/items/voice', {'raw_text': '测试'}, HTTP_X_WX_OPENID=openid)
        # 即使 LLM 解析失败，也应返回降级数据
        assert resp.status_code == 200
        assert 'items' in resp.json()['data']

    def test_barcode_entry_not_found(self, setup_family):
        client, openid, family_id = setup_family
        resp = client.post('/api/items/barcode', {'barcode': '000000'}, HTTP_X_WX_OPENID=openid)
        assert resp.status_code == 200
        assert resp.json()['found'] is False

    def test_operation_log_created(self, setup_family):
        client, openid, family_id = setup_family
        client.post('/api/items/create', {
            'name': '测试日志', 'quantity': 1, 'unit': '个',
            'expiry_date': str(date.today() + timedelta(days=7)),
            'days_to_expire': 7,
        }, HTTP_X_WX_OPENID=openid)
        resp = client.get('/api/logs', HTTP_X_WX_OPENID=openid)
        assert resp.status_code == 200
        assert len(resp.json()['results']['data']) > 0