#!/bin/bash
# 微信云托管启动脚本

set -e

# 数据库迁移
python manage.py migrate --settings=config.settings.prod

# 启动 gunicorn
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:80 \
    --workers 4 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -