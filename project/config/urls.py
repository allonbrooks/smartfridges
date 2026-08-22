from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('api/', include('apps.foods.urls')),
    path('api/', include('apps.recipes.urls')),
    path('api/', include('apps.shopping.urls')),
]