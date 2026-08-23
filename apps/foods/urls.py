from django.urls import path
from . import views

urlpatterns = [
    # 空间
    path('spaces', views.spaces_list, name='space-list-create'),
    path('spaces/<uuid:space_id>', views.space_detail, name='space-detail'),
    # 物品
    path('items/overview', views.item_overview, name='item-overview'),
    path('items', views.items_list, name='item-list-create'),
    path('items/batch', views.create_items_batch, name='item-batch-create'),
    path('items/barcode', views.barcode_entry, name='item-barcode'),
    path('items/voice', views.voice_entry, name='item-voice'),
    path('items/photo', views.photo_entry, name='item-photo'),
    path('items/<uuid:item_id>', views.item_detail, name='item-detail'),
    path('items/<uuid:item_id>/consume', views.consume_item, name='item-consume'),
    path('items/<uuid:item_id>/restore', views.restore_item, name='item-restore'),
    # 日志
    path('logs', views.list_logs, name='log-list'),
]