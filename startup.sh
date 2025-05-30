#!/bin/bash
set -e # Exit immediately if a command exits with a non-zero status.

# Install dependencies from the root requirements.txt
# This ensures gunicorn and other necessary packages are available for the startup script
echo "Installing dependencies from root requirements.txt..."
# Oryx build service usually handles this, this line can be commented out
# if dependencies are consistently installed by the build service.
# pip install -r requirements.txt

# Navigate to the Django project directory where manage.py is located
echo "Changing to timber_locator directory..."
cd timber_locator

# Run Django management commands
echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=timber_locator.production_settings
echo "Applying database migrations..."
python manage.py migrate --settings=timber_locator.production_settings

# Start Gunicorn
# Azure App Service will set the PORT environment variable
echo "Starting Gunicorn on 0.0.0.0:$PORT using production_settings..."
gunicorn timber_locator.wsgi:application --bind "0.0.0.0:$PORT" --workers 4 --env DJANGO_SETTINGS_MODULE=timber_locator.production_settings --timeout 120 --log-level debug
