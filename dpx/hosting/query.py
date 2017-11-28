from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet
from django.utils import timezone
from .exceptions import ValidationError
from .settings import DOTPODCAST_DOMAIN
import re


TAXONOMY_PATTERNS = {
    'Subject': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/subject/)#([\w-]+)$'),
    'Language': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/language/)#([\w-]+)$'),
    'Profanity': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/profanity/)#([\w-]+)$')
}


class PodcastQuerySet(QuerySet):
    @transaction.atomic()
    def ingest(self, url, data, keypair_generator=None):
        from .models import Author, Publisher, Term
        from .importing import download_file

        try:
            obj = self.get(remote_feed__iexact=url)
        except self.model.DoesNotExist:
            obj = self.model(remote_feed=url)

        owner_name = data.get('owner_name')
        owner_email = data.get('owner_email')

        if not owner_name or not owner_name.strip():
            raise ValidationError(
                'Owner name not provided.'
            )

        if not owner_email or not owner_email.strip():
            raise ValidationError(
                'Owner email not provided.'
            )

        User = apps.get_model(settings.AUTH_USER_MODEL)

        if ' ' in owner_name:
            first_name, last_name = owner_name.rsplit(' ', 1)
        else:
            first_name = owner_name
            last_name = ''

        try:
            user = User.objects.get(
                email__iexact=owner_email
            )
        except User.DoesNotExist:
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=owner_email,
                email=owner_email
            )

        try:
            obj.author = Author.objects.get(user=user)
        except Author.DoesNotExist:
            obj.author = Author.objects.create(
                name=user.get_full_name() or user.username,
                user=user
            )

        if not obj.pk:
            publisher_name = data.get('author')
            if not publisher_name or not publisher_name.strip():
                raise ValidationError(
                    'Publisher name not provided.'
                )

            try:
                publisher = Publisher.objects.get(
                    name__iexact=publisher_name
                )
            except Publisher.DoesNotExist:
                publisher = Publisher.objects.create(
                    name=publisher_name
                )

                publisher.admins.add(user)

            obj.publisher = publisher

        obj.name = data.get('title')
        obj.subtitle = data.get('subtitle')
        obj.copyright = data.get('copyright')
        obj.summary = data.get('summary')
        obj.description = data.get('description')

        artwork = data.get('image')
        if artwork and not obj.artwork:
            obj.remote_artwork = artwork

        obj.full_clean()
        obj.save()

        added_terms = []
        for term in data.get('taxonomy_terms', []):
            term = Term.objects.infer(term)
            obj.taxonomy_terms.add(term)
            added_terms.append(term.pk)

        obj.taxonomy_terms.remove(
            *obj.taxonomy_terms.exclude(
                pk__in=added_terms
            )
        )

        obj.episodes.ingest(
            data['items']
        )

        return obj


class TermQuerySet(QuerySet):
    def infer(self, url):
        from .models import Taxonomy

        for obj in self.filter(url__iexact=url):
            return obj

        for taxonomy, pattern in TAXONOMY_PATTERNS.items():
            match = pattern.match(url)
            if match is not None:
                tax_url, term_slug = match.groups()
                term_name = term_slug.replace('-', ' ').capitalize()

                try:
                    tax = Taxonomy.objects.get(url__iexact=tax_url)
                except Taxonomy.DoesNotExist:
                    tax = Taxonomy.objects.create(
                        name=taxonomy,
                        url=tax_url
                    )

                return self.create(
                    name=term_name,
                    url=url,
                    taxonomy=tax
                )

        raise ValidationError(
            'Third-party taxonomies are currently not supported.'
        )


class EpisodeQuerySet(QuerySet):
    def ingest(self, data):
        from dateutil.parser import parse as parse_date
        from .importing import download_file

        podcast = None

        for field, relation in self._known_related_objects.items():
            if podcast is not None:
                break

            for pk, obj in relation.items():
                if obj._meta.db_table == 'host_podcast':
                    podcast = obj
                    break

        for datum in data:
            try:
                episode = self.get(
                    remote_id=datum['id']
                )
            except self.model.DoesNotExist:
                episode = self.model(
                    remote_id=datum['id'],
                    podcast=podcast
                )

            episode.title = datum.get('title')
            episode.subtitle = datum.get('subtitle')
            episode.summary = datum.get('summary')
            episode.body = datum.get('description')
            episode.date_published = parse_date(datum['date'])

            artwork = datum.get('image')
            if artwork and not episode.artwork:
                episode.remote_artwork = artwork

            mimetype = datum['enclosure_type']
            duration = datum.get('enclosure_duration')

            if duration:
                parts = duration.split(':')
                if len(parts) == 3:
                    hours, minutes, seconds = [int(i) for i in parts]
                elif len(parts) == 2:
                    minutes, seconds = [int(i) for i in parts]
                    hours = 0
                else:
                    minutes, hours = 0, 0
                    seconds = int(duration)

                duration = (hours * 60 * 60) + (minutes * 60) + seconds

            if mimetype.startswith('audio/'):
                episode.remote_audio_enclosure = datum['enclosure_url']
                episode.audio_mimetype = datum['enclosure_type']
                episode.audio_filesize = datum['enclosure_size']

                if duration:
                    episode.audio_duration = duration
            elif mimetype.startswith('video/'):
                episode.remote_video_enclosure = datum['enclosure_url']
                episode.video_mimetype = datum['enclosure_type']
                episode.video_filesize = datum['enclosure_size']

                if duration:
                    episode.audio_duration = duration

            episode.full_clean()
            episode.save()

    def published(self):
        return self.filter(
            date_published__lte=timezone.now()
        )
