# scripts/seed_data.py
"""
初始化脚本：为新创建的家庭生成默认存储空间。

使用方式：在 FamilyGroup 创建后调用。
"""
from apps.foods.models import StorageSpace

DEFAULT_SPACES = [
    {'name': '冷藏区', 'zone_type': 'cold', 'icon': 'snowflake', 'sort_order': 1},
    {'name': '冷冻区', 'zone_type': 'frozen', 'icon': 'ice', 'sort_order': 2},
    {'name': '调料架', 'zone_type': 'normal', 'icon': 'flask', 'sort_order': 3},
    {'name': '零食柜', 'zone_type': 'normal', 'icon': 'cookie', 'sort_order': 4},
]


def create_default_spaces(family):
    """为家庭创建默认存储空间"""
    for space_data in DEFAULT_SPACES:
        StorageSpace.objects.get_or_create(
            family=family,
            name=space_data['name'],
            defaults=space_data
        )