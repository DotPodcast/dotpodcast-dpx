from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from ..models import Podcast, Episode
from . import PodcastMixin


class EpisodeListView(PodcastMixin, ListView):
    model = Episode
    paginate_by = 10

    def get_query_set(self):
        return super(EpisodeListView, self).get_query_set().live()

    def get_context_data(self, **kwargs):
        context = super(EpisodeListView, self).get_context_data(**kwargs)

        for podcast in Podcast.objects.all()[:1]:
            context['podcast'] = podcast

        return context


class EpisodeDetailView(PodcastMixin, DetailView):
    model = Episode

    def get_query_set(self):
        return super(EpisodeDetailView, self).get_query_set().live()

    def get_object(self):
        return self.model.objects.get(
            season__number=self.kwargs['season_number'],
            number=self.kwargs['episode_number']
        )
