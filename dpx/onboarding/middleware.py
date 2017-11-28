from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect


def onboarding_middleware(get_response):
    def middleware(request):
        from ..hosting.models import Podcast

        if not request.path.startswith('/onboarding/'):
            if not Podcast.objects.exists():
                return HttpResponseRedirect('/onboarding/')

        return get_response(request)

    return middleware
