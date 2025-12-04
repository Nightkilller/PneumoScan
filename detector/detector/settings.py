"""
Django settings for detector project.

Updated for local development:
 - MEDIA (uploads) configured
 - STATIC dirs configured
 - Templates dir added (project-level)
 - TIME_ZONE set to Asia/Kolkata
 - Basic console logging for easier debugging
"""

from pathlib import Path
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# Replace this before deploying to production.
SECRET_KEY = 'django-insecure-%mvncpakoh(#_wgswf87qhq0d%vb6)n4wq^iec4at41a^dyh#_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# During development allow localhost and 127.0.0.1
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'predict',   # your app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    # If you deploy, consider using WhiteNoise or proper static serving.
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'detector.urls'

# Templates: add a project-level templates/ folder and app template loading
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Project-level templates directory (create BASE_DIR / "templates" if you want shared templates)
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',  # makes `request` available in templates
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'detector.wsgi.application'

# Database - default sqlite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password validation (default)
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'   # updated to your timezone
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
# project-level static folder for development (create BASE_DIR / "static")
STATICFILES_DIRS = [BASE_DIR / "static"]
# STATIC_ROOT is used when you run collectstatic for deployment; keep it separate
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media (user uploads like the X-ray images)
MEDIA_URL = '/media/'
# Make MEDIA_ROOT an absolute path and ensure it exists
MEDIA_ROOT = BASE_DIR / "media"
os.makedirs(str(MEDIA_ROOT), exist_ok=True)

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Optional: adjust upload size limits (uncomment to enable)
# DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB
# FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10 MB

# Simple logging to console for development (helps debugging file paths etc.)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}