from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from ..models import Podcast, BlogPost
from . import PodcastMixin


class BlogPostListView(PodcastMixin, ListView):
    model = BlogPost
    paginate_by = 10

    def get_query_set(self):
        return super(BlogPostListView, self).get_query_set().live()

    def get_context_data(self, **kwargs):
        context = super(BlogPostListView, self).get_context_data(**kwargs)

        for podcast in Podcast.objects.all()[:1]:
            context['podcast'] = podcast

        return context


class BlogPostDetailView(PodcastMixin, DetailView):
    model = BlogPost

    def get_query_set(self):
        return super(BlogPostDetailView, self).get_query_set().live()
