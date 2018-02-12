from django.views.generic.detail import DetailView
from ..models import Page
from . import PodcastMixin


class PageDetailView(PodcastMixin, DetailView):
    model = Page

    def get_query_set(self):
        return super(PageDetailView, self).get_query_set().live()
