from django.urls import path
from . import views

urlpatterns = [
    path('users/login', views.login, name='user-login'),
    path('families', views.create_family, name='family-create'),
    path('families/join', views.join_family, name='family-join'),
    path('families/current', views.current_family, name='family-current'),
    path('families/<uuid:family_id>/members', views.family_members, name='family-members'),
    path('families/<uuid:family_id>/members/<uuid:user_id>', views.remove_member, name='family-remove-member'),
]