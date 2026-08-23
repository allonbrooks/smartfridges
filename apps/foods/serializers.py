from rest_framework import serializers
from .models import FoodItem, StorageSpace, BarcodeCache, OperationLog


class StorageSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StorageSpace
        fields = ['id', 'name', 'zone_type', 'icon', 'sort_order', 'created_at']
        read_only_fields = ['id', 'created_at']


class FoodItemSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    added_by_name = serializers.CharField(source='added_by.nickname', read_only=True, default='')
    space_name = serializers.CharField(source='storage_space.name', read_only=True, default='')

    class Meta:
        model = FoodItem
        fields = [
            'id', 'name', 'category', 'storage_space_id', 'space_name', 'barcode', 'icon',
            'quantity', 'unit', 'expiry_date', 'days_to_expire',
            'added_by', 'added_by_name', 'note', 'is_consumed',
            'consumed_at', 'status', 'days_remaining', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'added_by', 'is_consumed', 'consumed_at', 'created_at', 'updated_at']

    def get_status(self, obj):
        """计算红黄绿状态"""
        from datetime import date
        remaining = (obj.expiry_date - date.today()).days
        if remaining < 0:
            return 'red'
        elif remaining <= 3:
            return 'yellow'
        return 'green'

    def get_days_remaining(self, obj):
        from datetime import date
        return (obj.expiry_date - date.today()).days


class FoodItemCreateSerializer(serializers.ModelSerializer):
    """创建物品时使用，不需要计算字段"""
    quantity = serializers.IntegerField(default=1, min_value=1)
    expiry_date = serializers.DateField(required=False)
    days_to_expire = serializers.IntegerField(required=False, read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            'name', 'category', 'storage_space', 'barcode', 'icon',
            'quantity', 'unit', 'expiry_date', 'days_to_expire', 'note',
        ]

    def validate(self, attrs):
        from datetime import date, timedelta
        if 'expiry_date' not in attrs and 'days_to_expire' in attrs:
            attrs['expiry_date'] = date.today() + timedelta(days=attrs['days_to_expire'])
        if 'expiry_date' in attrs and 'days_to_expire' not in attrs:
            attrs['days_to_expire'] = (attrs['expiry_date'] - date.today()).days
        return attrs


class ConsumeSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(default=1, min_value=1)


class OperationLogSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True, default='')

    class Meta:
        model = OperationLog
        fields = ['id', 'user_id', 'user_nickname', 'action', 'item_name', 'detail', 'created_at']
