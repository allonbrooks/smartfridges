from django.urls import path
from . import views

urlpatterns = [
    # 空间
    path('spaces', views.list_spaces, name='space-list'),
    path('spaces/create', views.create_space, name='space-create'),
    path('spaces/<uuid:space_id>', views.space_detail, name='space-detail'),
    # 物品
    path('items/overview', views.item_overview, name='item-overview'),
    path('items', views.list_items, name='item-list'),
    path('items/create', views.create_item, name='item-create'),
    path('items/batch', views.create_items_batch, name='item-batch-create'),
    path('items/barcode', views.barcode_entry, name='item-barcode'),
    path('items/voice', views.voice_entry, name='item-voice'),
    path('items/<uuid:item_id>', views.item_detail, name='item-detail'),
    path('items/<uuid:item_id>/update', views.update_item, name='item-update'),
    path('items/<uuid:item_id>/consume', views.consume_item, name='item-consume'),
    path('items/<uuid:item_id>/restore', views.restore_item, name='item-restore'),
    path('items/<uuid:item_id>/delete', views.delete_item, name='item-delete'),
    # 日志
    path('logs', views.list_logs, name='log-list'),
]