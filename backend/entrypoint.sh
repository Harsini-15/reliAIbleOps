#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! nc -z $POSTGRES_HOST ${POSTGRES_PORT:-5432}; do
  sleep 0.5
done
echo "PostgreSQL started."

echo "Making migrations..."
python manage.py makemigrations accounts ingestion validation anomaly_detection alerts --noinput

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput 2>/dev/null || true

# Create superuser if it doesn't exist
python manage.py shell -c "
from accounts.models import UserAccount
if not UserAccount.objects.filter(username='admin').exists():
    UserAccount.objects.create_superuser('admin', 'admin@reliableops.io', 'admin123', role='admin')
    print('Superuser created: admin / admin123')
else:
    print('Superuser already exists.')
"

echo "Starting server..."
exec gunicorn reliableops.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
