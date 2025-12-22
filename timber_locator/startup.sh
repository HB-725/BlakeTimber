#!/bin/bash
set -e

# Always run from the deployed app folder
cd /home/site/wwwroot

echo "PORT=$PORT"
echo "SQLITE_PATH=$SQLITE_PATH"
echo "MEDIA_ROOT=$MEDIA_ROOT"

# Activate the Oryx-created virtualenv (name from your logs: antenv)
source /home/site/wwwroot/antenv/bin/activate

# (Optional) static + migrations
python manage.py collectstatic --noinput
python manage.py migrate --noinput

# Start gunicorn on Azure-required port
gunicorn --bind 0.0.0.0:${PORT} --workers 2 timber_locator.wsgi:application
