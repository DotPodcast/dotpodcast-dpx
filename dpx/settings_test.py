from fakeredis import FakeRedis, FakeStrictRedis
from .core import realtime
from .settings import *
import django_rq.queues
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'test'
    }
}

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '..', 'media')

django_rq.queues.get_redis_connection = lambda _, strict: (
    FakeStrictRedis() if strict else FakeRedis()
)

RQ_QUEUES['default']['ASYNC'] = False

def push(message, *channels):
    pass

realtime.push = push

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'ERROR',
        'handlers': ['null']
    },
    'handlers': {
        'null': {
            'class': 'logging.NullHandler'
        }
    },
    'loggers': {
        'dpx.hosting': {
            'handlers': ['null']
        }
    }
}
