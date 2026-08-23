# apps/shopping/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('shopping-list', views.shopping_list, name='shopping-list'),
    path('shopping-list/<uuid:item_id>', views.shopping_item_detail, name='shopping-item-detail'),
    path('shopping-list/clear-checked', views.clear_checked, name='shopping-clear-checked'),
]