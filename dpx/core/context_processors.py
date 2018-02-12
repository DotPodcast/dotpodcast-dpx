from django.conf import settings
from .. import __version__


def meta(request):
    return {
        'DPX_VERSION': __version__,
        'DOMAIN': settings.DOMAIN
    }
