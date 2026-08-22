from django.urls import path
from . import views

urlpatterns = [
    path('recipes/generate', views.generate_recipe_view, name='recipe-generate'),
]