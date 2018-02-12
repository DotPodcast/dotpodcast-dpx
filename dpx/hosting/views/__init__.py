from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from ..models import Podcast, Page, BlogPost


class PodcastMixin(object):
    def get_context_data(self, **kwargs):
        context = super(PodcastMixin, self).get_context_data(**kwargs)

        for podcast in Podcast.objects.all()[:1]:
            context['podcast'] = podcast

        menu_items = [
            {
                'url': '/',
                'title': _('Home')
            }
        ]

        for page in Page.objects.all():
            menu_items.append(
                {
                    'url': page.get_absolute_url(),
                    'title': page.title
                }
            )

        if BlogPost.objects.live():
            menu_items.append(
                {
                    'url': reverse('blog_post_list'),
                    'title': _('Blog')
                }
            )

        context['menu_items'] = menu_items
        return context
