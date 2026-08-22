from rest_framework import serializers


class RecipeGenerateSerializer(serializers.Serializer):
    item_ids = serializers.ListField(child=serializers.UUIDField(), min_length=1)
    preferences = serializers.CharField(required=False, allow_blank=True, default='')