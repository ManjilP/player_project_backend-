#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Convert static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
python manage.py shell -c "from accounts.models import User; User.objects.filter(email='admin@futslab.com').exists() or User.objects.create_superuser('admin@futslab.com', 'Admin', 'Admin@123')"
