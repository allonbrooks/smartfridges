import pymysql
pymysql.install_as_MySQLdb()

# 微信云托管 MySQL 5.7，但 Django 4.2+ 要求 8.0，绕过版本检查
from django.db.backends.mysql import features
features.DatabaseFeatures.minimum_database_version = (5, 7, 0)