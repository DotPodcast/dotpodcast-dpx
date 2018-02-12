from django_blockstack_auth import urls as blockstack_urls
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.static import serve
from .hosting import urls as hosting_urls
from .onboarding import urls as onboarding_urls


urlpatterns = [
    url(r'^onboarding/', include(onboarding_urls)),
    url(r'^', include(hosting_urls)),
    url(r'^blockstack/', include(blockstack_urls, namespace='blockstack'))
]

if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns() + [
        url(
            r'^media/(?P<path>.*)$', serve,
            {
                'document_root': settings.MEDIA_ROOT
            }
        )
    ]
