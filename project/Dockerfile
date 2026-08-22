# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码
COPY . .

# 收集静态文件
RUN python manage.py collectstatic --noinput --settings=config.settings.prod

# 启动
EXPOSE 80
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "4", "--timeout", "60"]