from django.core.management.base import BaseCommand
from ...exceptions import ImportingHTTPError
from ...importing import get_feed_stream, import_feed
from ...models import Podcast
import requests


class Command(BaseCommand):
    args = '<feed feed ...>'

    def add_arguments(self, parser):
        parser.add_argument(
            'args',
            nargs='+',
            type=str,
            help='The feeds to ingest'
        )

    def handle(self, *args, **options):
        for url in args:
            try:
                stream = get_feed_stream(url)
            except ImportingHTTPError as ex:
                self.stderr.write(str(ex))
                continue

            feed = import_feed(stream)
            url = feed.get('link') or url

            podcast = Podcast.objects.ingest(url, feed)
