from django.conf import settings as site_settings
from django.db import models
from . import helpers, query, settings


class Person(models.Model):
    slug = models.CharField(max_length=36, unique=True)
    name = models.CharField(max_length=100)
    url = models.URLField('URL', max_length=500, null=True, blank=True)
    avatar = models.ImageField(
        max_length=64,
        upload_to=helpers.upload_avatar,
        null=True,
        blank=True
    )

    public_key = models.CharField(
        max_length=500, db_index=True, null=True, blank=True
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = helpers.create_slug(
                type(self).objects,
                self.pk is None,
                self.name
            )

        super(Person, self).save(*args, **kwargs)

    def as_dict(self, ssl=False):
        def get_url():
            from django.contrib.sites.models import Site
            from django.core.urlresolvers import reverse

            site = Site.objects.get_current()
            return 'http%s://%s%s' % (
                ssl and 's' or '',
                site.domain,
                reverse('author', args=[self.slug])
            )

        return {
            'name': self.name,
            'url': self.url or get_url(),
            'avatar': (
                self.avatar and
                self.avatar.url or
                'https://gravatar.com/avatar?s=300&d=mm'
            )
        }

    class Meta:
        ordering = ('name',)


class Author(Person):
    user = models.OneToOneField(site_settings.AUTH_USER_MODEL, related_name='author')


class Taxonomy(models.Model):
    name = models.CharField(max_length=300)
    url = models.URLField('URL', max_length=500, unique=True)
    description = models.TextField(null=True, blank=True)
    required = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Term(models.Model):
    taxonomy = models.ForeignKey(Taxonomy, related_name='terms')
    name = models.CharField(max_length=300)
    url = models.URLField('URL', max_length=500, unique=True)
    description = models.TextField(null=True, blank=True)

    objects = query.TermQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Host(Person):
    user = models.OneToOneField(
        site_settings.AUTH_USER_MODEL, related_name='host', null=True, blank=True
    )


class Podcast(models.Model):
    name = models.CharField(max_length=300)
    subtitle = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        Author, related_name='podcasts', null=True, blank=True
    )

    artwork = models.ImageField(
        max_length=255,
        upload_to=helpers.upload_podcast_artwork,
        null=True,
        blank=True
    )

    banner_image = models.URLField(max_length=500, null=True, blank=True)
    publisher_name = models.CharField(max_length=300)
    publisher_url = models.URLField('URL', max_length=500, null=True, blank=True)
    publisher_logo = models.URLField(max_length=500, null=True, blank=True)
    admins = models.ManyToManyField(site_settings.AUTH_USER_MODEL, related_name='publishers')
    hosts = models.ManyToManyField(Host, through='PodcastHost')
    taxonomy_terms = models.ManyToManyField(Term, related_name='podcasts')

    objects = query.PodcastQuerySet.as_manager()

    def __str__(self):
        return self.name

    def get_description_plain(self):
        from bs4 import BeautifulSoup

        return ' '.join(
            BeautifulSoup(
                self.description,
                'html.parser'
            ).findAll(text=True)
        ).strip()

    def get_next_url(self, page, ssl=False):
        from django.utils.http import urlencode

        if page.has_next():
            return '%s?%s' % (
                self.get_feed_url(ssl=ssl),
                urlencode(
                    {
                        'page': page.next_page_number()
                    }
                )
            )

    def get_home_page_url(self, ssl=False):
        return helpers.absolute_url(
            '/%s/' % self.slug,
            ssl=ssl
        )

    def get_feed_url(self, ssl=False):
        from django.core.urlresolvers import reverse

        return helpers.absolute_url(
            reverse('podcast_feed', args=[self.slug]),
            ssl=ssl
        )

    def get_subscription_url(self, ssl=False):
        from django.core.urlresolvers import reverse

        return helpers.absolute_url(
            reverse('podcast_subscribe', args=[self.slug])
        )

    def as_dict(self, page=1, ssl=False):
        from django.core.paginator import (
            Paginator, EmptyPage, PageNotAnInteger
        )

        paginator = Paginator(
            self.episodes.select_related().prefetch_related().published(),
            settings.EPISODES_PER_PAGE
        )

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        ext = {
            'version': settings.DOTPODCAST_VERSION,
            'subscription_url': self.get_subscription_url(ssl=ssl),
            'subtitle': self.subtitle,
            'taxonomy_terms': list(
                self.taxonomy_terms.values_list(
                    'url', flat=True
                )
            ),
            'artwork': {
                '@1x': (
                    self.artwork and
                    self.artwork.url or
                    None
                ),
                '@2x': (
                    self.artwork and
                    self.artwork.url or
                    None
                )
            },
            'description_text': self.get_description_plain(),
            'description_html': self.description
        }

        data = {
            'version': settings.JSONFEED_VERSION,
            'title': self.name,
            'home_page_url': self.get_home_page_url(ssl=ssl),
            'feed_url': self.get_feed_url(ssl=ssl),
            'description': self.subtitle,
            'user_comment': settings.USER_COMMENT,
            'author': self.author and self.author.as_dict() or None,
            'expired': False,
            '_dotpodcast': ext,
            'items': [
                episode.as_dict(ssl=ssl) for episode in page_obj.object_list
            ]
        }

        next_url = self.get_next_url(page_obj, ssl=ssl)
        if next_url:
            data['next_url'] = next_url

        return data

    def dump_json(self, stream, page=1, ssl=False):
        import json

        json.dump(
            self.as_dict(page=page, ssl=ssl),
            stream,
            ensure_ascii=False,
            indent=4
        )

    def subscribe(self, kind, token, app_name='', app_url='', app_logo=''):
        for subscription in self.subscribers.filter(source_token=token):
            return subscription

        return self.subscribers.create(
            source_token=token
        )

    class Meta:
        ordering = ('name',)


class PodcastHost(models.Model):
    podcast = models.ForeignKey(Podcast)
    host = models.ForeignKey(Host, related_name='podcasts')
    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('host', 'podcast')


class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Season(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='seasons')
    name = models.CharField(max_length=100)
    number = models.PositiveIntegerField()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('number',)


class Episode(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='episodes')
    remote_id = models.CharField(
        'remote ID', max_length=512, null=True, blank=True, db_index=True
    )

    slug = models.CharField(max_length=100, editable=False)
    title = models.CharField(max_length=500)
    subtitle = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)

    artwork = models.ImageField(
        max_length=124,
        upload_to=helpers.upload_episode_artwork,
        null=True,
        blank=True
    )

    remote_artwork = models.URLField(
        null=True,
        blank=True
    )

    banner_image = models.URLField(max_length=500, null=True, blank=True)
    date_published = models.DateTimeField()
    date_modified = models.DateTimeField(
        auto_now=True, null=True, blank=True
    )

    audio_enclosure = models.FileField(
        max_length=255, null=True, blank=True,
        upload_to=helpers.upload_episode_enclosure
    )

    audio_mimetype = models.CharField(max_length=50, null=True, blank=True)
    audio_duration = models.PositiveIntegerField()
    audio_filesize = models.PositiveIntegerField()

    video_enclosure = models.FileField(
        max_length=255, null=True, blank=True,
        upload_to=helpers.upload_episode_enclosure
    )

    video_mimetype = models.CharField(max_length=50, null=True, blank=True)
    audio_duration = models.PositiveIntegerField()
    audio_filesize = models.PositiveIntegerField()

    season = models.ForeignKey(
        Season, related_name='episodes', null=True, blank=True
    )

    number = models.PositiveIntegerField(default=0)
    hosts = models.ManyToManyField(Host, through='EpisodeHost')
    taxonomy_terms = models.ManyToManyField(Term, related_name='episodes')

    objects = query.EpisodeQuerySet.as_manager()

    def __str__(self):
        return self.title

    def download(self, kind):
        if kind == 'audio' and self.audio_enclosure:
            return {
                'url': self.audio_enclosure.url,
                'mime_type': self.audio_mimetype,
                'file_size': self.audio_filesize
            }

        if kind == 'video' and self.video_enclosure:
            return {
                'url': self.video_enclosure.url,
                'mime_type': self.video_mimetype,
                'file_size': self.video_filesize
            }

        raise Exception('Unknown media kind')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = helpers.create_slug(
                self.podcast.episodes,
                self.pk is None,
                self.title
            )

        super(Episode, self).save(*args, **kwargs)

    def get_page_url(self, ssl=False):
        return helpers.absolute_url(
            '/%s/' % self.slug,
            ssl=ssl
        )

    def get_body_plain(self):
        from bs4 import BeautifulSoup

        return ' '.join(
            BeautifulSoup(
                self.body,
                'html.parser'
            ).findAll(text=True)
        ).strip()

    def get_download_url(self, kind):
        from django.core.urlresolvers import reverse

        return helpers.absolute_url(
            reverse(
                'episode_download',
                args=[kind]
            )
        )

    def as_dict(self, ssl=False):
        ext = {}

        if self.subtitle:
            ext['subtitle'] = self.subtitle

        if self.season:
            ext['season_number'] = self.season.number

        if self.number:
            ext['episode_number'] = self.number

        if self.audio_enclosure:
            ext['content_audio'] = {
                'mime_type': self.audio_mimetype,
                'duration': self.audio_duration,
                'url': self.get_download_url('audio'),
                'file_size': self.audio_filesize
            }

        if self.video_enclosure:
            ext['content_video'] = {
                'mime_type': self.video_mimetype,
                'duration': self.video_duration,
                'url': self.get_download_url('video'),
                'file_size': self.video_filesize
            }

        data = {
            'id': self.get_page_url(ssl=ssl),
            'url': self.get_page_url(ssl=ssl),
            'title': self.title,
            'content_text': self.get_body_plain(),
            'content_html': self.body,
            'summary': self.summary,
            'date_published': self.date_published.replace(
                microsecond=0
            ).isoformat(),
            'author': self.podcast.author.as_dict(),
            '_dotpodcast': ext
        }

        if self.artwork:
            data['image'] = self.artwork.url

        if self.date_modified:
            data['date_modified'] = self.date_modified.replace(
                microsecond=0
            ).isoformat()

        return data

    class Meta:
        unique_together = ('slug', 'podcast')
        ordering = ('-date_published',)
        get_latest_by = 'date_published'


class EpisodeHost(models.Model):
    episode = models.ForeignKey(Episode)
    host = models.ForeignKey(Host, related_name='hosted_episodes')
    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('host', 'episode')


class EpisodeGuest(models.Model):
    episode = models.ForeignKey(Episode)
    person = models.ForeignKey(Person, related_name='guesting_episodes')
    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('person', 'episode')


class Subscriber(models.Model):
    podcast = models.ForeignKey(Podcast, related_name='subscribers')
    source_token = models.CharField(max_length=255, unique=True)
    public_token = models.CharField(max_length=32, unique=True)
    secret_token = models.CharField(max_length=128, unique=True)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name or self.token

    def save(self, *args, **kwargs):
        if not self.public_token:
            self.public_token = helpers.create_token(32)

        if not self.secret_token:
            self.secret_token = helpers.create_token(128, True)

        super(Subscriber, self).save(*args, **kwargs)

    def as_dict(self):
        return {
            'subscriber_hash': self.source_token,
            'subscriber_secret': self.secret_token
        }

    class Meta:
        ordering = ('-last_fetched', '-date_subscribed')
