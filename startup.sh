#!/bin/bash
set -e

# Oryx extracts the app to a temp dir and sets APP_PATH.
APP_DIR="${APP_PATH:-/home/site/wwwroot}"

echo "APP_DIR=$APP_DIR"
echo "PORT=$PORT"
echo "SQLITE_PATH=$SQLITE_PATH"
echo "MEDIA_ROOT=$MEDIA_ROOT"

cd "$APP_DIR"

# Activate venv created by Oryx inside the extracted app directory
if [ -f "$APP_DIR/antenv/bin/activate" ]; then
  source "$APP_DIR/antenv/bin/activate"
elif [ -f "/tmp/8de416ce654ec63/antenv/bin/activate" ]; then
  # fallback (rarely needed, but safe)
  source "/tmp/8de416ce654ec63/antenv/bin/activate"
else
  echo "ERROR: Cannot find antenv/bin/activate under $APP_DIR"
  ls -la
  exit 1
fi

# If manage.py is inside a subfolder (like timber_locator/), cd into it
if [ -f "manage.py" ]; then
  PROJECT_DIR="."
elif [ -f "timber_locator/manage.py" ]; then
  PROJECT_DIR="timber_locator"
else
  echo "ERROR: manage.py not found"
  find . -maxdepth 3 -name "manage.py" -print || true
  exit 1
fi

cd "$PROJECT_DIR"

python manage.py collectstatic --noinput
python manage.py migrate --noinput

gunicorn timber_locator.wsgi:application --bind 0.0.0.0:${PORT} --workers 2
