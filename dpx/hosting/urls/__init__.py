from django.conf.urls import url, include
from ..views import pages
from . import authors, admin, podcasts, episodes, blog


urlpatterns = [
    url(r'^admin/', include(admin)),
    url(r'^authors/', include(authors)),
    url(r'^', include(podcasts)),
    url(r'^', include(episodes)),
    url(r'^blog/', include(blog)),
    url(
        r'^(?P<slug>[\w-]+)/$',
        pages.PageDetailView.as_view(), name='page_detail'
    )
]
