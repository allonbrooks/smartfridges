FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput --settings=config.settings.prod
EXPOSE 80
CMD ["sh", "-c", "python manage.py migrate --settings=config.settings.prod && exec gunicorn config.wsgi:application --bind 0.0.0.0:80 --workers 4 --timeout 60 --access-logfile - --error-logfile -"]