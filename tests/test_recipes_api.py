import pytest
from datetime import date, timedelta
from rest_framework.test import APIClient
from apps.users.models import User, FamilyGroup, Member
from apps.foods.models import FoodItem, StorageSpace


@pytest.fixture
def setup_data():
    client = APIClient()
    client.post('/api/users/login', HTTP_X_WX_OPENID='recipe_user')
    client.post('/api/families', {'name': '食谱家庭'}, HTTP_X_WX_OPENID='recipe_user')
    # 创建食材
    family = FamilyGroup.objects.first()
    from datetime import date
    item1 = FoodItem.objects.create(
        family=family, name='番茄', category='vegetable',
        quantity=2, unit='个', expiry_date=date.today() + timedelta(days=7),
        days_to_expire=7
    )
    item2 = FoodItem.objects.create(
        family=family, name='鸡蛋', category='dairy',
        quantity=3, unit='个', expiry_date=date.today() + timedelta(days=10),
        days_to_expire=10
    )
    return client, 'recipe_user', [str(item1.id), str(item2.id)]


@pytest.mark.django_db
class TestRecipeAPI:
    def test_generate_recipe_requires_login(self):
        client = APIClient()
        resp = client.post('/api/recipes/generate', {'item_ids': []})
        assert resp.status_code == 401

    def test_generate_recipe_missing_items(self, setup_data):
        client, openid, _ = setup_data
        resp = client.post('/api/recipes/generate', {'item_ids': ['00000000-0000-0000-0000-000000000000']}, HTTP_X_WX_OPENID=openid)
        assert resp.status_code == 400

    def test_generate_recipe_returns_structure(self, setup_data):
        client, openid, item_ids = setup_data
        resp = client.post('/api/recipes/generate', {'item_ids': item_ids}, HTTP_X_WX_OPENID=openid)
        assert resp.status_code == 200
        data = resp.json()['data']['recipe']
        assert 'title' in data
        assert 'ingredients' in data
        assert 'steps' in data