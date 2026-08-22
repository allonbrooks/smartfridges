# 微信云托管专用 Dockerfile
# 项目代码在 project/ 子目录下
FROM python:3.11-slim

WORKDIR /app

# 安装 Python 依赖
COPY project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY project/ .

# 收集静态文件
RUN python manage.py collectstatic --noinput --settings=config.settings.prod

EXPOSE 80
CMD ["sh", "-c", "python manage.py migrate --settings=config.settings.prod && exec gunicorn config.wsgi:application --bind 0.0.0.0:80 --workers 4 --timeout 60 --access-logfile - --error-logfile -"]