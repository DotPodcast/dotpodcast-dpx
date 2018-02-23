import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = os.getenv('SECRET_KEY')
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_blockstack_auth',
    'bootstrap3',
    'datetimewidget',
    'django_rq',
    'markdown_deux',
    'taggit',
    'dpx.core',
    'dpx.onboarding',
    'dpx.hosting',
    'dpx.theming'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'dpx.onboarding.middleware.onboarding_middleware'
]

if DEBUG:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': True,
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler'
            }
        },
        'loggers': {
            'django': {
                'level': 'INFO',
                'handlers': ['console'],
                'propagate': True
            },
            'django.db.backends': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False
            },
            'dpx.hosting': {
                'level': 'DEBUG',
            }
        }
    }

ROOT_URLCONF = 'dpx.urls'
SITE_ID = 1

THEME = 'default'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'themes', THEME, 'templates'),
            os.path.join(BASE_DIR, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'dpx.core.context_processors.meta',
                'dpx.theming.context_processors.theming'
            ]
        }
    }
]

WSGI_APPLICATION = 'dpx.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres',
        'HOST': 'db',
        'PORT': 5432
    }
}

REDIS_URL = os.getenv('REDIS_URL', 'redis://redis:6379')
RQ_QUEUES = {
    'default': {
        'HOST': 'redis',
        'PORT': 6379,
        'DB': 0,
        'DEFAULT_TIMEOUT': 360
    }
}

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
    }
]

AUTHENTICATION_BACKENDS = [
    'django_blockstack_auth.backends.BlockstackBackend'
]

LANGUAGE_CODE = 'en'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

STATICFILES_DIRS = (
    'themes/%s/static' % THEME,
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder'
)

MEDIA_URL = '/media/'
MEDIA_ROOT = '/media/'

LOGIN_URL = '/blockstack/login/'
LOGIN_REDIRECT_URL = '/admin/import/'

DROPBOX_API_KEY = os.getenv('DROPBOX_API_KEY')
DROPBOX_API_SECRET = os.getenv('DROPBOX_API_SECRET')

DOMAIN = os.getenv(
    'DOMAIN',
    os.getenv('WEB_1_ENV_DOCKERCLOUD_CONTAINER_FQDN', 'localhost')
)

THUNDERPUSH_DOMAIN = os.getenv(
    'THUNDERPUSH_DOMAIN',
    os.getenv('WS_1_ENV_DOCKERCLOUD_CONTAINER_FQDN', DOMAIN)
)

THUNDERPUSH_PORT = 8080
THUNDERPUSH_PUBLIC_KEY = os.getenv('PUBLIC_KEY')
THUNDERPUSH_PRIVATE_KEY = os.getenv('PRIVATE_KEY')
