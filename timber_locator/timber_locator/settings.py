import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# App Service provides WEBSITE_HOSTNAME when running in Azure.
AZURE_HOSTNAME = os.environ.get("WEBSITE_HOSTNAME")
IN_AZURE = bool(AZURE_HOSTNAME)


def _split_env_list(name):
    raw = os.environ.get(name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "your-secret-key-here")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get("DJANGO_DEBUG", "False" if IN_AZURE else "True") == "True"


ALLOWED_HOSTS = _split_env_list("DJANGO_ALLOWED_HOSTS")
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["localhost", "127.0.0.1", "[::1]", "blaketimber.com", "www.blaketimber.com"]
    if AZURE_HOSTNAME:
        ALLOWED_HOSTS.append(AZURE_HOSTNAME)

CSRF_TRUSTED_ORIGINS = _split_env_list("DJANGO_CSRF_TRUSTED_ORIGINS")
if not CSRF_TRUSTED_ORIGINS:
    CSRF_TRUSTED_ORIGINS = [
        "https://www.blaketimber.com",
        "https://blaketimber.com",
    ]
    if AZURE_HOSTNAME:
        CSRF_TRUSTED_ORIGINS.append(f"https://{AZURE_HOSTNAME}")

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],  # Only use console for local development
            'level': 'INFO',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.template': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}


# Application definition

INSTALLED_APPS = [
    'crispy_forms',
    'crispy_bootstrap5',
    'mptt',
    'django_htmx',  # Changed from 'htmx' to 'django_htmx' which is the correct package name
    'inventory',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "inventory.middleware.ProxyHeaderDebugMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "timber_locator.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',   
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'inventory', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'inventory.context_processors.categories',
            ],
        },
    },
]

WSGI_APPLICATION = "timber_locator.wsgi.application"


# Database
# --- Persistent paths on Azure App Service ---
# On Azure Linux App Service, /home is persistent storage.
AZURE_HOME = "/home/site"

SQLITE_PATH = os.environ.get("SQLITE_PATH")
if not SQLITE_PATH and IN_AZURE:
    SQLITE_PATH = f"{AZURE_HOME}/db.sqlite3"
DB_NAME = SQLITE_PATH or str(BASE_DIR / "db.sqlite3")  # local default

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DB_NAME,
    }
}



# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get("STATIC_ROOT") or os.path.join(BASE_DIR, "staticfiles")

# Remove STATICFILES_DIRS since we're using app-level static directories
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'),
# ]

# Media files
MEDIA_URL = "/media/"
if os.environ.get("MEDIA_ROOT"):
    MEDIA_ROOT = Path(os.environ["MEDIA_ROOT"])
elif IN_AZURE:
    MEDIA_ROOT = Path(f"{AZURE_HOME}/media")
else:
    MEDIA_ROOT = BASE_DIR / "media"


# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Security settings (safe defaults in production).
# Azure App Service already enforces HTTPS; avoid redirect loops at the app level.
SECURE_SSL_REDIRECT = (
    False
    if IN_AZURE
    else (not DEBUG and os.environ.get("DJANGO_SECURE_SSL_REDIRECT", "True") == "True")
)
SESSION_COOKIE_SECURE = (
    not DEBUG and os.environ.get("DJANGO_SESSION_COOKIE_SECURE", "True") == "True"
)
CSRF_COOKIE_SECURE = (
    not DEBUG and os.environ.get("DJANGO_CSRF_COOKIE_SECURE", "True") == "True"
)


SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
