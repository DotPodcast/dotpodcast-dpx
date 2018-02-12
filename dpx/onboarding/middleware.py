from django.contrib.auth.models import User
from django.http.response import HttpResponseRedirect


def onboarding_middleware(get_response):
    def middleware(request):
        from ..hosting.models import Podcast

        if not request.path.startswith('/onboarding/'):
            if not Podcast.objects.exists():
                return HttpResponseRedirect('/onboarding/')

            # if Podcast.objects.filter(dropbox_api__isnull=True).exists():
            #     return HttpResponseRedirect('/onboarding/dropbox/')

        return get_response(request)

    return middleware
