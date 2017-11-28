from django.conf.urls import url, include
from .core import urls as core_urls
from .onboarding import urls as onboarding_urls


urlpatterns = [
    url(r'^', include(core_urls)),
    url(r'^onboarding/', include(onboarding_urls))
]
