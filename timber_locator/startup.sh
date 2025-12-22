#!/bin/bash
set -e

echo "PORT=$PORT"
echo "SQLITE_PATH=$SQLITE_PATH"
echo "MEDIA_ROOT=$MEDIA_ROOT"

python -m pip install -r requirements.txt
python manage.py collectstatic --noinput
python manage.py migrate --noinput

gunicorn --bind 0.0.0.0:${PORT} --workers 2 timber_locator.wsgi:application
