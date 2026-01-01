#!/bin/bash
set -e

# Oryx may extract the app to a temp dir and set APP_PATH.
APP_DIR="${APP_PATH:-/home/site/wwwroot}"

echo "APP_DIR=$APP_DIR"
echo "PORT=${PORT:-8000}"
echo "SQLITE_PATH=$SQLITE_PATH"
echo "MEDIA_ROOT=$MEDIA_ROOT"

cd "$APP_DIR"
echo "Now in: $(pwd)"
echo "Contents:"
ls -la | head -n 80

# Prefer python3 on App Service
PY=python3

# 1) Try activate Oryx venv if it exists (optional)
if [ -f "$APP_DIR/antenv/bin/activate" ]; then
  echo "Using Oryx venv: $APP_DIR/antenv"
  source "$APP_DIR/antenv/bin/activate"
  PY=python
else
  echo "No Oryx venv found. Installing deps with pip --user."
  # Ensure pip exists
  $PY -m ensurepip --upgrade 2>/dev/null || true
  $PY -m pip install --upgrade pip

  # Install requirements into user site-packages
  $PY -m pip install --user -r requirements.txt

  # Make sure user installs are discoverable
  export PATH="$HOME/.local/bin:$PATH"
  USER_SITE="$($PY -c 'import site; print(site.getusersitepackages())')"
  export PYTHONPATH="$USER_SITE:$PYTHONPATH"

  echo "PATH=$PATH"
  echo "PYTHONPATH=$PYTHONPATH"
fi

# 2) Locate manage.py
if [ -f "manage.py" ]; then
  PROJECT_DIR="."
elif [ -f "timber_locator/manage.py" ]; then
  PROJECT_DIR="timber_locator"
else
  echo "ERROR: manage.py not found under $APP_DIR"
  find . -maxdepth 4 -name "manage.py" -print || true
  exit 1
fi

cd "$PROJECT_DIR"
echo "Project dir: $(pwd)"

# 3) Run Django tasks
$PY manage.py migrate --noinput
$PY manage.py collectstatic --noinput

# 4) Start server
exec gunicorn timber_locator.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 2
