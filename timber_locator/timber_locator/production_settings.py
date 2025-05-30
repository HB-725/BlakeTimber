"""
Production settings for Azure deployment
"""
import os
from .settings import *
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Security settings for production
DEBUG = False

# Azure App Service sets WEBSITE_HOSTNAME
ALLOWED_HOSTS = [
    os.environ.get('WEBSITE_HOSTNAME', 'localhost'),
    'localhost',
    '127.0.0.1',
]

# Database configuration for Azure PostgreSQL
if 'AZURE_POSTGRESQL_HOST' in os.environ:
    # Azure portal sets these environment variables automatically
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('AZURE_POSTGRESQL_NAME', 'blaketimber-database'),
            'USER': os.environ.get('AZURE_POSTGRESQL_USER'),
            'PASSWORD': os.environ.get('AZURE_POSTGRESQL_PASSWORD'),
            'HOST': os.environ.get('AZURE_POSTGRESQL_HOST'),
            'PORT': os.environ.get('AZURE_POSTGRESQL_PORT', '5432'),
            'OPTIONS': {
                'sslmode': 'require',
            },
        }
    }
elif 'DATABASE_URL' in os.environ:
    # Fallback for manual DATABASE_URL configuration
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(os.environ['DATABASE_URL'])
    }
else:
    # Keep SQLite for local development
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Static files configuration for Azure
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Use WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files for Azure Blob Storage (optional)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security settings
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging for Azure
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
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
