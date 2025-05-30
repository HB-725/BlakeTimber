#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Start Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 timber_locator.wsgi:application
