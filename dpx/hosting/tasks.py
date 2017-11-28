from django.db import transaction
from .helpers import get_remote_feed


@transaction.atomic()
def fetch_feed(podcast_pk, url):
    from ..validator.utils import find_validator
    from .models import Podcast
    import requests
    import json

    response = requests.get(url, stream=True)
    response.raise_for_status()
    response.raw.decode_content = True
    feed = json.load(response.raw)

    validator_cls = find_validator(feed)
    validator = validator_cls(feed)
    validator.validate()

    if validator.errors:
        raise Exception('Feed is invalid.')
