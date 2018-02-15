from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
import sys


class Command(BaseCommand):
    def handle(self, *args, **options):
        db_conn = connections['default']

        try:
            c = db_conn.cursor()
        except OperationalError:
            sys.exit(1)
