#!/bin/bash

# Navigate to the Django project directory
cd timber_locator

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput --settings=timber_locator.production_settings

# Run database migrations
python manage.py migrate --settings=timber_locator.production_settings

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 timber_locator.wsgi:application --env DJANGO_SETTINGS_MODULE=timber_locator.production_settings
