import pymysql
pymysql.install_as_MySQLdb()

# 微信云托管 MySQL 5.7，但 Django 4.2+ 要求 8.0，绕过版本检查
import django.db.backends.mysql.base
_orig_get_new_connection = django.db.backends.mysql.base.DatabaseWrapper.get_new_connection

def _patched_get_new_connection(self, conn_params):
    conn = _orig_get_new_connection(self, conn_params)
    conn.server_version = (8, 0, 0)  # 告知 Django 使用 8.0 特性
    return conn

django.db.backends.mysql.base.DatabaseWrapper.get_new_connection = _patched_get_new_connection