from pathlib import Path
import sys

import environ


BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
env.read_env(BASE_DIR.parent / '.env')

SECRET_KEY = env.str('DJANGO_SECRET_KEY', 'SECRET_KEY')

DEBUG = env.bool('DJANGO_DEBUG', True)
TESTING = 'test' in sys.argv

ALLOWED_HOSTS = env.list(
    'DJANGO_ALLOWED_HOSTS',
    default=['127.0.0.1', 'localhost'],
)

INTERNAL_IPS = env.list(
    'DJANGO_INTERNAL_IPS',
    default=['127.0.0.1'],
)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'users.apps.UsersConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG and not TESTING:
    INSTALLED_APPS.insert(-1, 'debug_toolbar')

    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
        *MIDDLEWARE,
    ]

ROOT_URLCONF = 'referal.urls'

TEMPLATES_DIRS = [
    BASE_DIR / 'templates',
]
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': TEMPLATES_DIRS,
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

WSGI_APPLICATION = 'referal.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'OPTIONS': {
                'pool': True,
            },
            'HOST': env.str('POSTGRES_HOST', 'postgresql'),
            'PORT': env.str('POSTGRES_PORT', '5432'),
            'USER': env.str('POSTGRES_USER', 'user'),
            'PASSWORD': env.str('POSTGRES_PASSWORD', 'password'),
            'NAME': env.str('POSTGRES_DB', 'database'),
        },
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': (
            'django.contrib.auth.password_validation'
            '.UserAttributeSimilarityValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.MinimumLengthValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.CommonPasswordValidator'
        ),
    },
    {
        'NAME': (
            'django.contrib.auth.password_validation.NumericPasswordValidator'
        ),
    },
]

LANGUAGE_CODE = 'ru'
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / 'static/'

STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static_dev',
]

MEDIA_URL = 'media/'

MEDIA_ROOT = BASE_DIR / 'media/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

RABBITMQ_HOST = env.str('RABBITMQ_HOST', 'localhost')
RABBITMQ_PORT = env.int('RABBITMQ_PORT', 15672)
RABBITMQ_USER = env.str('RABBITMQ_DEFAULT_USER', 'localhost')
RABBITMQ_PASSWORD = env.str('RABBITMQ_DEFAULT_PASS', 'localhost')

REDIS_HOST = env.str('REDIS_HOST', 'localhost')
REDIS_PORT = env.int('REDIS_PORT', 6379)
REDIS_DB = env.int('REDIS_DB', 0)
REDIS_PASSWORD = env.str('REDIS_PASSWORD', 'default')
REDIS_USER = env.str('REDIS_USER', 'redis')
REDIS_USER_PASSWORD = env.str('REDIS_USER_PASSWORD', 'redis')

REDIS_USER_PHONE_EXPIRATION_TIME = 10 * 60
