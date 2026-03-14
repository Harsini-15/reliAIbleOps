#!/bin/bash
set -e

echo "Setting up Backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Running migrations..."
python manage.py migrate

echo "Creating superuser if not exists..."
python manage.py shell -c "
from accounts.models import UserAccount
if not UserAccount.objects.filter(username='admin').exists():
    UserAccount.objects.create_superuser('admin', 'admin@reliableops.io', 'admin123', role='admin')
    print('Superuser created: admin / admin123')
"

echo "Starting Backend Server on port 8000..."
python manage.py runserver 0.0.0.0:8000 &
BACKEND_PID=$!

echo "Setting up Frontend..."
cd ../frontend
npm install

echo "Starting Frontend Server on port 5173..."
npm run dev -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo "Ready! Backend running on http://localhost:8000, Frontend running on http://localhost:5173"
echo "Press Ctrl+C to stop both."

wait $BACKEND_PID
wait $FRONTEND_PID
