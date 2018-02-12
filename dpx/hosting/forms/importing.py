from django import forms
from django.utils.translation import ugettext_lazy as _
from ..importing import get_feed_stream, import_feed
from ..models import Podcast
from ...core import realtime
import django_rq
import logging
import time


def start(url):
    time.sleep(3)

    try:
        stream = get_feed_stream(url)
        feed = import_feed(stream)
        Podcast.objects.ingest(url, feed, async=True)
    except Exception, ex:
        logging.getLogger('dpx.hosting').error(
            'Error starting import',
            exc_info=True
        )

        realtime.push(
            {
                'import': {
                    'error': unicode(ex)
                }
            },
            'django-rq'
        )


class ImportForm(forms.Form):
    url = forms.URLField(
        max_length=512,
        label=_('RSS feed URL'),
        help_text=_(
            'Enter the URL to your RSS feed to import it into DPX'
        )
    )

    def save(self):
        url = self.cleaned_data['url']
        return django_rq.enqueue(start, url)
