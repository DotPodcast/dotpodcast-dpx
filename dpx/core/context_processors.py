from django.conf import settings
from .. import __version__


def meta(request):
    return {
        'DPX_VERSION': __version__,
        'DOMAIN': settings.DOMAIN,
        'DEBUG': settings.DEBUG,
        'THUNDERPUSH_PORT': settings.THUNDERPUSH_PORT,
        'THUNDERPUSH_PUBLIC_KEY': settings.THUNDERPUSH_PUBLIC_KEY
    }
