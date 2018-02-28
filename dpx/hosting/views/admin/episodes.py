from django.conf import settings
from django.core.urlresolvers import reverse
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.utils.translation import ugettext_lazy as _
from . import AdminViewMixin, FileFormMixin
from ...models import Episode, Season
from ...forms.episodes import EpisodeForm


class EpisodeListView(AdminViewMixin, ListView):
    model = Episode
    template_name = 'hosting/admin/episode_list.html'
    menu_item_name = 'episodes'

    def get_query_set(self):
        return super(EpisodeListView, self).get_query_set().live()


class EpisodeFormMixin(FileFormMixin, AdminViewMixin):
    model = Episode
    template_name = 'hosting/admin/episode_form.html'
    menu_item_name = 'episodes'
    form_class = EpisodeForm
    file_fields = (
        'audio_enclosure',
        'video_enclosure',
        'artwork',
        'banner_image'
    )

    def get_query_set(self):
        return super(EpisodeFormMixin, self).get_query_set().live()

    def get_success_url(self):
        return reverse('admin_update_episode', args=[self.object.pk])


class CreateEpisodeFormView(EpisodeFormMixin, CreateView):
    def get_initial(self):
        initial = super(CreateEpisodeFormView, self).get_initial()
        for season in Season.objects.all()[:1]:
            number = season.episodes.count() + 1
            initial['title'] = _('Episode %d') % number
            initial['season'] = season
            initial['number'] = number

        return initial


class UpdateEpisodeFormView(EpisodeFormMixin, UpdateView):
    pass


class DeleteEpisodeView(AdminViewMixin, DeleteView):
    menu_item_name = 'episodes'
    template_name = 'hosting/admin/episode_delete.html'
    model = Episode

    def get_query_set(self):
        return super(DeleteEpisodeView, self).get_query_set().live()

    def get_success_url(self):
        return reverse('admin_episode_list')
