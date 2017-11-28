from django.conf.urls import url, include
from . import authors, podcasts

urlpatterns = [
    url(r'^authors/', include(authors)),
    url(r'^(?P<podcast_slug>[\w]+)/', include(podcasts))
]
