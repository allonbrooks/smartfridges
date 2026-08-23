#!/bin/bash
# 微信云托管启动脚本

set -e

# 自动创建数据库（如果不存在）
python -c "
import pymysql, os
addr = os.getenv('MYSQL_ADDRESS', '').split(':')
host = addr[0] or os.getenv('DB_HOST', 'localhost')
port = int(addr[1]) if len(addr) > 1 else int(os.getenv('DB_PORT', '3306'))
user = os.getenv('MYSQL_USERNAME', os.getenv('DB_USER', 'root'))
password = os.getenv('MYSQL_PASSWORD', os.getenv('DB_PASSWORD', ''))
db = os.getenv('DB_NAME', 'fridge')
conn = pymysql.connect(host=host, port=port, user=user, password=password)
conn.cursor().execute(f'CREATE DATABASE IF NOT EXISTS \`{db}\` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci')
conn.close()
"

# 数据库迁移
python manage.py migrate --settings=config.settings.prod

# 启动 gunicorn
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:80 \
    --workers 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -