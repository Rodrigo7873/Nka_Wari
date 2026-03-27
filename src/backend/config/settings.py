"""
Django settings for N'Ka Wari project.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# =============================================================================
# ENVIRONNEMENT & SÉCURITÉ (à configurer via variables d'environnement en prod)
# =============================================================================
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-dev-key-change-in-production')
DEBUG = True  # Mode DEV local réactivé

ALLOWED_HOSTS = ['tonusername.pythonanywhere.com', '127.0.0.1', 'localhost', '10.0.2.2', '*']
CSRF_TRUSTED_ORIGINS = ['https://tonusername.pythonanywhere.com']

# Session persistante ultra-compatible
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 30  # 30 jours
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = False  # Plus permissif pour persistance émulateur
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_NAME = 'nk_wari_session'
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
PIN_SESSION_TIMEOUT = SESSION_COOKIE_AGE

# Supabase Settings
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')

# =============================================================================
# APPLICATIONS
# =============================================================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

LOCAL_APPS = [
    'modules.core',
    'modules.dettes',
    'modules.karfa',
    'modules.comptes',
    'modules.parametres',
]

THIRD_PARTY_APPS = [
    'django.contrib.humanize',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

# =============================================================================
# MIDDLEWARE
# =============================================================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'modules.core.middleware.PinMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# =============================================================================
# URLS & TEMPLATES
# =============================================================================
ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.parent / 'frontend/templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'modules.core.context_processors.notifications_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# =============================================================================
# BASE DE DONNÉES
# =============================================================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# =============================================================================
# VALIDATION DES MOTS DE PASSE
# =============================================================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =============================================================================
# INTERNATIONALISATION
# =============================================================================
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# =============================================================================
# FICHIERS STATIQUES & MEDIA
# =============================================================================
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR.parent / 'frontend/static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR.parent / 'frontend/media'

# =============================================================================
# DIVERS
# =============================================================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'