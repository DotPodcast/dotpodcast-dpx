from django.core.management.base import BaseCommand
from ...exceptions import ImportingHTTPError
from ...models import Podcast
import codecs
import requests
import sys


class Command(BaseCommand):
    args = '<slug slug ...>'

    def add_arguments(self, parser):
        parser.add_argument(
            'args',
            nargs='+',
            type=str,
            help='The slug of the podcast to export'
        )

    def handle(self, *args, **options):
        writer = codecs.getwriter('UTF-8')
        for podcast in Podcast.objects.filter(slug__in=args):
            podcast.dump_json(
                writer(sys.stdout)
            )
