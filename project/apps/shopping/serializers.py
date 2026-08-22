# apps/shopping/serializers.py
from rest_framework import serializers
from .models import ShoppingList


class ShoppingListSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.nickname', read_only=True, default='')

    class Meta:
        model = ShoppingList
        fields = ['id', 'item_name', 'quantity', 'unit', 'reason', 'is_purchased',
                  'created_by_id', 'created_by_name', 'created_at', 'purchased_at']
        read_only_fields = ['id', 'is_purchased', 'created_by_id', 'created_at', 'purchased_at']


class MarkPurchasedSerializer(serializers.Serializer):
    is_purchased = serializers.BooleanField()