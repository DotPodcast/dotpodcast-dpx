from django.conf.urls import url
from ..views.episodes import EpisodeListView, EpisodeDetailView


urlpatterns = [
    url(r'^$', EpisodeListView.as_view(), name='episode_list'),
    url(
        r'^(?P<season_number>\d)(?P<episode_number>\d{2})/$',
        EpisodeDetailView.as_view(),
        name='episode_detail'
    )
]
