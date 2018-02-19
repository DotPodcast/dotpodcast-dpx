from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt
from ..views.podcasts import *


urlpatterns = [
    url(r'^head\.json$', FeedHeadView.as_view(), name='podcast_feed_head'),
    url(r'^body\.json$', FeedBodyView.as_view(), name='podcast_feed_body'),
    url(r'^rss\.xml$', RSSFeedView.as_view(), name='podcast_feed_rss'),
    url(
        r'subscribe\.json$',
        csrf_exempt(SubscribeView.as_view()),
        name='podcast_subscribe'
    ),
    url(
        r'^download-(?P<kind>audio|video)\.json$',
        DownloadView.as_view(),
        name='episode_download'
    )
]
