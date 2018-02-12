from django.conf.urls import url
from ..views.authors import *

urlpatterns = [
    url(r'^(?P<slug>[\w-]+)/$', AuthorDetailView.as_view(), name='author'),
]
