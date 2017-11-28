from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect


def onboarding_middleware(get_response):
    def middleware(request):
        if not request.path.startswith('/onboarding/'):
            if not User.objects.filter(is_superuser=True).exists():
                return HttpResponseRedirect('/onboarding/')

        return get_response(request)

    return middleware
