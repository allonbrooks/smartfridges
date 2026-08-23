import os
from .base import *

DEBUG = False
ALLOWED_HOSTS = ['*']

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# 微信云托管使用 MYSQL_ADDRESS(host:port) / MYSQL_USERNAME / MYSQL_PASSWORD 标准命名
_mysql_addr = os.getenv('MYSQL_ADDRESS', '').split(':')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('DB_NAME', 'fridge'),
        'USER': os.getenv('MYSQL_USERNAME', os.getenv('DB_USER', 'root')),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', os.getenv('DB_PASSWORD', '')),
        'HOST': _mysql_addr[0] if _mysql_addr[0] else os.getenv('DB_HOST', 'localhost'),
        'PORT': _mysql_addr[1] if len(_mysql_addr) > 1 else os.getenv('DB_PORT', '3306'),
    }
}