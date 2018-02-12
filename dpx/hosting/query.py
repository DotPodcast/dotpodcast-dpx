from django.apps import apps
from django.conf import settings
from django.db import transaction
from django.db.models import QuerySet, Q
from django.utils import timezone
from .exceptions import ValidationError
from .settings import DOTPODCAST_DOMAIN
import re
import string


TAXONOMY_PATTERNS = {
    'Subject': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/subject/)#([\w-]+)$'),
    'Language': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/language/)#([\w-]+)$'),
    'Profanity': re.compile(r'^(https?://' + DOTPODCAST_DOMAIN + '/taxonomies/profanity/)#([\w-]+)$')
}


class ContentObjectQuerySet(QuerySet):
    def live(self):
        return self.filter(state='a')


class PodcastQuerySet(QuerySet):
    def ingest(self, url, data, slug=None):
        from urlparse import urlparse, urlunparse, urljoin
        from .models import Author, Term
        from .importing import download_file

        u = lambda url: urlunparse(urlparse(url)).replace(' ', '%20')

        with transaction.atomic():
            obj = self.model.objects.select_for_update().get()
            obj.subtitle = obj.subtitle or data.get('subtitle')
            obj.description = obj.description or data.get('description')

            artwork = data.get('image')
            if artwork and not obj.artwork:
                obj.artwork = download_file(
                    urljoin(
                        u(url),
                        u(artwork)
                    ),
                    as_django_file=True
                )

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

        obj.episodes.ingest(data['items'])
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
    @transaction.atomic()
    def _ingest(self, podcast, datum):
        from dateutil.parser import parse as parse_date
        from urlparse import urlparse, urlunparse, urljoin
        from .importing import download_file

        u = lambda url: urlunparse(urlparse(url)).replace(' ', '%20')
        enclosure_url = u(datum['enclosure_url'])
        if not enclosure_url.startswith('http://') and not enclosure_url.startswith('https://'):
            return

        published = parse_date(datum['date'])
        if not published:
            return

        try:
            episode = self.select_for_update().get(
                podcast=podcast,
                title=datum.get('title') or '(Untitled)',
                date_published=published
            )
        except self.model.DoesNotExist:
            episode = self.model(
                podcast=podcast,
                title=datum.get('title') or '(Untitled)',
                date_published=published
            )

        episode.subtitle = datum.get('subtitle')
        episode.summary = datum.get('summary')
        episode.body = datum.get('description')

        if datum.get('season'):
            try:
                episode.season = podcast.seasons.get(
                    number=datum['season']
                )
            except podcast.seasons.model.DoesNotExist:
                episode.season = podcast.seasons.create(
                    number=datum['season']
                )
        else:
            episode.season = podcast.seasons.last()

        if datum.get('episode'):
            episode.number = datum['episode']
        else:
            episode.number = episode.season.episodes.count() + 1

        episode.kind = datum.get('episode_type')

        if not episode.number_bonus:
            same_numbered_episodes = podcast.episodes.filter(
                season=episode.season,
                number=episode.number,
                kind=episode.kind
            )

            if episode.pk:
                same_numbered_episodes = same_numbered_episodes.exclude(
                    pk=episode.pk
                )

            episode.number_bonus = same_numbered_episodes.count() + 1

        try:
            episode.date_published = published
        except:
            return

        if not episode.date_published.tzinfo:
            episode.date_published = episode.date_published.replace(
                tzinfo=timezone.utc
            )

        if not episode.artwork:
            artwork = datum.get('image')
            if artwork:
                episode.artwork = download_file(
                    urljoin(
                        (
                            datum['url'] and u(datum['url']) or
                            datum['id'] and u(datum['id'])
                        ),
                        u(artwork)
                    ),
                    as_django_file=True
                )

            mimetype = datum['enclosure_type'](enclosure_url)
            filesize = datum['enclosure_size']()
            duration = datum['enclosure_duration'](filesize)
            parts = str(duration).split(':')

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
                episode.audio_enclosure = download_file(enclosure_url, True)
                episode.audio_mimetype = mimetype
                episode.audio_filesize = filesize
                episode.audio_duration = duration
            elif mimetype.startswith('video/'):
                episode.video_enclosure = download_file(enclosure_url, True)
                episode.video_mimetype = mimetype
                episode.video_filesize = filesize
                episode.audio_duration = duration
            else:
                return

        episode.full_clean()
        episode.save()

    def ingest(self, data):
        from dateutil.parser import parse as parse_date

        podcast = None
        for field, relation in self._known_related_objects.items():
            if podcast is not None:
                break

            for pk, obj in relation.items():
                if obj._meta.db_table == 'hosting_podcast':
                    podcast = obj
                    break

        if podcast is None:
            return

        data = sorted(data, key=lambda i: parse_date(i['date']))

        for datum in data:
            self._ingest(podcast, datum)

    def published(self):
        return self.filter(
            date_published__lte=timezone.now()
        )

    def letter_to_number(self, letter):
        return string.lowercase.find(letter) + 1


class PageQuerySet(ContentObjectQuerySet):
    def choices(self):
        def children(parent=None, indent=0):
            for (pk, name) in self.filter(
                parent=parent
            ).values_list(
                'pk',
                'title'
            ):
                yield (pk, ('- ' * indent) + name)
                for child in children(pk, indent + 1):
                    yield child

        for (pk, name) in children():
            yield (pk, name)


class BlogPostQuerySet(ContentObjectQuerySet):
    def live(self):
        return super(BlogPostQuerySet, self).live().filter(
            date_published__lte=timezone.now()
        )
