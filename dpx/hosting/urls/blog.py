from django.conf.urls import url
from ..views.blog import BlogPostListView, BlogPostDetailView


urlpatterns = [
    url(r'^$', BlogPostListView.as_view(), name='blog_post_list'),
    url(
        r'^(?P<slug>[\w-]+)/$',
        BlogPostDetailView.as_view(),
        name='blog_post_detail'
    )
]
