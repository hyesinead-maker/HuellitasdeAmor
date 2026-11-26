"""
Django settings for HuellistasdeAmor.
Configuracion para desarrollo local y Render.
"""

import os
from pathlib import Path

import dj_database_url


# ==========================================
# DIRECTORIO PRINCIPAL
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ==========================================
# CONFIGURACION DE SEGURIDAD
# ==========================================

EN_RENDER = os.environ.get('RENDER') == 'true'

DEBUG = not EN_RENDER

if EN_RENDER:
    SECRET_KEY = os.environ['SECRET_KEY']
else:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY',
        'django-insecure-solo-desarrollo-local'
    )


ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'huellitasdeamor.onrender.com',
]

RENDER_EXTERNAL_HOSTNAME = os.environ.get(
    'RENDER_EXTERNAL_HOSTNAME'
)

if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


CSRF_TRUSTED_ORIGINS = [
    'https://huellitasdeamor.onrender.com',
]

if RENDER_EXTERNAL_HOSTNAME:
    CSRF_TRUSTED_ORIGINS.append(
        f'https://{RENDER_EXTERNAL_HOSTNAME}'
    )


# ==========================================
# APLICACIONES
# ==========================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'cloudinary_storage',
    'cloudinary',

    'mascotas',
]


# ==========================================
# MIDDLEWARE
# ==========================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'huellitas.urls'


# ==========================================
# PLANTILLAS HTML
# ==========================================

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'huellitas.wsgi.application'


# ==========================================
# BASE DE DATOS
# ==========================================

if EN_RENDER:

    DATABASES = {
        'default': dj_database_url.parse(
            os.environ['DATABASE_URL'],
            conn_max_age=600,
        )
    }

else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# ==========================================
# VALIDACION DE CONTRASENAS
# ==========================================

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


# ==========================================
# IDIOMA Y ZONA HORARIA
# ==========================================

LANGUAGE_CODE = 'es-mx'

TIME_ZONE = 'America/Mexico_City'

USE_I18N = True

USE_TZ = True


# ==========================================
# ARCHIVOS ESTATICOS
# ==========================================

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = []

if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')


# ==========================================
# ARCHIVOS MULTIMEDIA
# ==========================================

MEDIA_URL = '/media/'

MEDIA_ROOT = BASE_DIR / 'media'


# ==========================================
# ALMACENAMIENTO
# ==========================================

if EN_RENDER:

    STORAGES = {
        'default': {
            'BACKEND': 'cloudinary_storage.storage.MediaCloudinaryStorage',
        },
        'staticfiles': {
            'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
        },
    }

else:

    STORAGES = {
        'default': {
            'BACKEND': 'django.core.files.storage.FileSystemStorage',
        },
        'staticfiles': {
            'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage',
        },
    }


# ==========================================
# CORREO ELECTRONICO
# ==========================================

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


# ==========================================
# SEGURIDAD EN PRODUCCION
# ==========================================

if EN_RENDER:

    SECURE_PROXY_SSL_HEADER = (
        'HTTP_X_FORWARDED_PROTO',
        'https'
    )

    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True


# ==========================================
# CAMPO AUTOMATICO PREDETERMINADO
# ==========================================

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
