from django.conf.urls import url
from .views import EpisodeListView


urlpatterns = [
    url(r'^$', EpisodeListView.as_view(), name='home'),
]
