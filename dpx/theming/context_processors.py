from django.conf import settings


def theming(request):
    return {
        'THEME_BASE': 'themes/%s/templates/base.html' % settings.THEME
    }
