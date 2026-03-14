web: daphne futsal_management.asgi:application --port $PORT --bind 0.0.0.0
worker: celery -A futsal_management worker --loglevel=info
