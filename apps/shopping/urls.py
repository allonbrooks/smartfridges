# apps/shopping/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('shopping-list', views.list_shopping, name='shopping-list'),
    path('shopping-list/add', views.add_shopping_item, name='shopping-add'),
    path('shopping-list/<uuid:item_id>/purchased', views.mark_purchased, name='shopping-purchased'),
    path('shopping-list/<uuid:item_id>/delete', views.delete_shopping_item, name='shopping-delete'),
    path('shopping-list/clear-checked', views.clear_checked, name='shopping-clear-checked'),
]