"""
条码查询服务。

优先查本地缓存，缓存未命中时返回空（由前端降级为手动输入）。
"""
import logging
from datetime import date
from apps.foods.models import BarcodeCache

logger = logging.getLogger(__name__)


def lookup_barcode(barcode: str) -> dict:
    """
    查询条码信息。

    返回: {'name': str, 'default_expiry_days': int, 'category': str, 'icon': str, 'found': bool}
    """
    try:
        cached = BarcodeCache.objects.get(barcode=barcode)
        cached.query_count += 1
        cached.save(update_fields=['query_count', 'last_queried'])
        return {
            'name': cached.name,
            'default_expiry_days': cached.default_expiry_days,
            'category': cached.category,
            'icon': cached.icon,
            'found': True,
        }
    except BarcodeCache.DoesNotExist:
        return {'found': False}


def cache_barcode(barcode: str, name: str, expiry_days: int = 7,
                  category: str = 'other', icon: str = ''):
    """缓存条码查询结果"""
    BarcodeCache.objects.update_or_create(
        barcode=barcode,
        defaults={
            'name': name,
            'default_expiry_days': expiry_days,
            'category': category,
            'icon': icon,
        }
    )