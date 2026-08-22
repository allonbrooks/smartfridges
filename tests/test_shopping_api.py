# project/tests/test_shopping_api.py
import pytest
from rest_framework.test import APIClient
from apps.shopping.models import ShoppingList


@pytest.mark.django_db
class TestShoppingAPI:
    def test_add_shopping_item(self):
        client = APIClient()
        client.post('/api/users/login', HTTP_X_WX_OPENID='shop_user')
        client.post('/api/families', {'name': '购物测试'}, HTTP_X_WX_OPENID='shop_user')
        resp = client.post('/api/shopping-list/add', {
            'item_name': '鸡蛋', 'quantity': 2, 'unit': '盒'
        }, HTTP_X_WX_OPENID='shop_user', content_type='application/json')
        assert resp.status_code == 201
        assert resp.json()['data']['item_name'] == '鸡蛋'

    def test_list_shopping(self):
        client = APIClient()
        client.post('/api/users/login', HTTP_X_WX_OPENID='shop_user2')
        client.post('/api/families', {'name': '购物测试2'}, HTTP_X_WX_OPENID='shop_user2')
        resp = client.get('/api/shopping-list', HTTP_X_WX_OPENID='shop_user2')
        assert resp.status_code == 200

    def test_mark_purchased(self):
        client = APIClient()
        client.post('/api/users/login', HTTP_X_WX_OPENID='shop_user3')
        client.post('/api/families', {'name': '购物测试3'}, HTTP_X_WX_OPENID='shop_user3')
        client.post('/api/shopping-list/add', {
            'item_name': '牛奶', 'quantity': 1, 'unit': '瓶'
        }, HTTP_X_WX_OPENID='shop_user3', content_type='application/json')
        item_id = ShoppingList.objects.first().id
        resp = client.patch(
            f'/api/shopping-list/{item_id}/purchased',
            {'is_purchased': True},
            HTTP_X_WX_OPENID='shop_user3',
            content_type='application/json'
        )
        assert resp.status_code == 200
        assert ShoppingList.objects.get(id=item_id).is_purchased