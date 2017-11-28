from base64 import b64encode
from hashlib import md5
from os import path
import random
import string


def upload_avatar(instance, filename):
    return 'people/%s%s' % (
        md5(instance.slug).hexdigest(),
        path.splitext(filename)[-1]
    )


def upload_podcast_artwork(instance, filename):
    return 'podcasts/%s/artwork%s' % (
        md5(instance.slug).hexdigest(),
        path.splitext(filename)[-1]
    )


def upload_episode_artwork(instance, filename):
    return 'podcasts/%s/%s%s' % (
        md5(instance.podcast.slug).hexdigest(),
        md5(instance.slug).hexdigest(),
        path.splitext(filename)[-1]
    )


def upload_episode_enclosure(instance, filename):
    return 'podcasts/%s/%s%s' % (
        md5(instance.podcast.slug).hexdigest(),
        md5(instance.slug).hexdigest(),
        path.splitext(filename)[-1]
    )


def create_slug(queryset, new, name):
    from django.template.defaultfilters import slugify
    from django.utils.timezone import now
    from hashlib import md5

    base = slugify(name).replace('-', '')
    if not base:
        return md5(now().isoformat())

    slug = base
    if new:
        i = 1

        while queryset.filter(slug=slug).exists():
            slug = '%s-%d' % (base, i)
            i += 1

    return slug


def create_keypair():
    from os import chmod
    from Crypto.PublicKey import RSA

    key = RSA.generate(2048)
    return (
        pubkey.exportKey('OpenSSH'),
        key.exportKey('PEM')
    )


def create_token(length, include_punctuation=False):
    characters = ''

    while len(characters) < length:
        characters += string.digits + string.letters

        if include_punctuation:
            characters += string.punctuation

    return b64encode(
        ''.join(
            random.sample(characters, length)
        )
    )

def absolute_url(url, ssl=False):
    from django.contrib.sites.models import Site
    from urllib.parse import urljoin

    site = Site.objects.get_current()
    base = 'http%s://%s/' % (
        (ssl and 's' or ''),
        site.domain
    )

    return urljoin(base, url)
