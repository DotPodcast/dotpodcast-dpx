from django.core.urlresolvers import reverse
from django.views.generic.edit import UpdateView
from . import AdminViewMixin, FileFormMixin
from ...forms.podcasts import PodcastForm
from ...models import Podcast


class PodcastFormView(FileFormMixin, AdminViewMixin, UpdateView):
    model = Podcast
    form_class = PodcastForm
    template_name = 'hosting/admin/podcast_form.html'
    file_fields = ('artwork', 'banner_image')
    menu_item_name = 'settings'

    def get_object(self):
        return Podcast.objects.first()

    def get_success_url(self):
        return reverse('admin_podcast_settings')
