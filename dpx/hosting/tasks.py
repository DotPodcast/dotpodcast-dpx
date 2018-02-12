from django.db import transaction
from mutagen.mp3 import MP3
from os import path


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


@transaction.atomic()
def set_audio_duration(episode_id):
    from .models import Episode

    episode = Episode.objects.select_for_update().get(pk=episode_id)
    if not episode.audio_enclosure:
        return

    mp3 = MP3(episode.audio_enclosure.path)
    episode.audio_duration = mp3.info.length
    episode.save(update_fields=('audio_duration',))


@transaction.atomic()
def set_audio_filesize(episode_id):
    from .models import Episode

    episode = Episode.objects.select_for_update().get(pk=episode_id)
    if not episode.audio_enclosure:
        return

    episode.audio_filesize = path.getsize(episode.audio_enclosure.path)
    episode.save(update_fields=('audio_filesize',))


def set_video_duration(episode_id):
    "Not implemented yet"


def set_video_filesize(episode_id):
    from .models import Episode

    episode = Episode.objects.select_for_update().get(pk=episode_id)
    if not episode.video_enclosure:
        return

    episode.video_filesize = path.getsize(episode.video_enclosure.path)
    episode.save(update_fields=('video_filesize',))
