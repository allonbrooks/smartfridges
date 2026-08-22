import pytest
from apps.users.models import User, FamilyGroup, Member
from apps.foods.models import StorageSpace, FoodItem, BarcodeCache, OperationLog
from apps.shopping.models import ShoppingList


@pytest.mark.django_db
class TestUserModels:
    def test_create_user(self):
        user = User.objects.create(openid='test_openid', nickname='测试用户')
        assert user.nickname == '测试用户'
        assert user.openid == 'test_openid'

    def test_create_family_group(self):
        user = User.objects.create(openid='owner')
        family = FamilyGroup.objects.create(name='我的家', invite_code='ABC123', created_by=user)
        assert family.name == '我的家'
        assert family.invite_code == 'ABC123'

    def test_create_member(self):
        user = User.objects.create(openid='member1')
        family = FamilyGroup.objects.create(name='我的家', invite_code='DEF456')
        member = Member.objects.create(user=user, family=family, role=Member.Role.ADMIN)
        assert member.role == Member.Role.ADMIN
        assert str(member) == f'{user.nickname} @ {family.name}'


@pytest.mark.django_db
class TestFoodModels:
    def test_create_storage_space(self):
        family = FamilyGroup.objects.create(name='测试家庭', invite_code='SPACE1')
        space = StorageSpace.objects.create(
            family=family, name='冷藏区', zone_type=StorageSpace.ZoneType.COLD
        )
        assert space.zone_type == 'cold'
        assert str(space) == f'{family.name} - {space.name}'

    def test_create_food_item(self):
        family = FamilyGroup.objects.create(name='测试家庭', invite_code='FOOD1')
        space = StorageSpace.objects.create(family=family, name='冷藏区', zone_type='cold')
        from datetime import date, timedelta
        item = FoodItem.objects.create(
            family=family, name='牛奶', category=FoodItem.Category.DAIRY,
            storage_space=space, quantity=2, unit='盒',
            expiry_date=date.today() + timedelta(days=7), days_to_expire=7
        )
        assert item.quantity == 2
        assert item.category == 'dairy'

    def test_barcode_cache(self):
        BarcodeCache.objects.create(
            barcode='6901234567890', name='纯牛奶', default_expiry_days=7
        )
        cached = BarcodeCache.objects.get(barcode='6901234567890')
        assert cached.name == '纯牛奶'
        assert cached.query_count == 0


@pytest.mark.django_db
class TestShoppingList:
    def test_create_shopping_item(self):
        family = FamilyGroup.objects.create(name='测试家庭', invite_code='SHOP1')
        item = ShoppingList.objects.create(
            family=family, item_name='鸡蛋', quantity=2, unit='盒'
        )
        assert item.item_name == '鸡蛋'
        assert not item.is_purchased


@pytest.mark.django_db
class TestSeedData:
    def test_create_default_spaces(self):
        from scripts.seed_data import create_default_spaces
        family = FamilyGroup.objects.create(name='种子测试', invite_code='SEED01')
        create_default_spaces(family)
        spaces = family.storage_spaces.all()
        assert spaces.count() == 4
        names = [s.name for s in spaces]
        assert '冷藏区' in names
        assert '冷冻区' in names