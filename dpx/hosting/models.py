from django.conf import settings as site_settings
from django.db import models, transaction
from django.utils.translation import ugettext_lazy as _
from taggit.managers import TaggableManager
from uuid import uuid4
from . import helpers, query, settings, tasks
import django_rq
import string


class ContentObject(models.Model):
    state = models.CharField(
        max_length=1,
        choices=(
            ('a', 'active'),
            ('t', 'trashed')
        ),
        default='a',
        editable=False
    )

    date_modified = models.DateTimeField(
        auto_now=True, null=True, blank=True, editable=False
    )

    objects = query.ContentObjectQuerySet.as_manager()

    def restore(self):
        self.state = 'a'
        self.save()

    class Meta:
        abstract = True


class Person(ContentObject):
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

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = helpers.create_slug(
                type(self).objects,
                self.pk is None,
                self.name
            )

        super(Person, self).save(*args, **kwargs)

    def as_dict(self, request):
        def get_url():
            from django.contrib.sites.models import Site
            from django.core.urlresolvers import reverse

            return request.build_absolute_uri(
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
    user = models.OneToOneField(
        site_settings.AUTH_USER_MODEL,
        related_name='author',
        null=True,
        on_delete=models.SET_NULL
    )


class Taxonomy(models.Model):
    name = models.CharField(max_length=300)
    url = models.URLField('URL', max_length=500, unique=True)
    description = models.TextField(null=True, blank=True)
    required = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Term(models.Model):
    taxonomy = models.ForeignKey(
        Taxonomy,
        related_name='terms',
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=300)
    url = models.URLField('URL', max_length=500, unique=True)
    description = models.TextField(null=True, blank=True)

    objects = query.TermQuerySet.as_manager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


class Host(Person):
    user = models.OneToOneField(
        site_settings.AUTH_USER_MODEL,
        related_name='host',
        null=True,
        on_delete=models.SET_NULL
    )


class Podcast(ContentObject):
    name = models.CharField(max_length=300)
    subtitle = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    author = models.ForeignKey(
        Author,
        related_name='podcasts',
        null=True,
        on_delete=models.SET_NULL
    )

    artwork = models.ImageField(
        max_length=255,
        upload_to=helpers.upload_podcast_artwork,
        null=True,
        blank=True
    )

    banner_image = models.ImageField(
        upload_to=helpers.upload_banner,
        max_length=255, null=True, blank=True
    )

    publisher_name = models.CharField(max_length=300)
    publisher_url = models.URLField(
        'publisher URL', max_length=500, null=True, blank=True
    )

    publisher_logo = models.URLField(max_length=500, null=True, blank=True)
    admins = models.ManyToManyField(
        site_settings.AUTH_USER_MODEL,
        related_name='publishers'
    )

    hosts = models.ManyToManyField(Host, through='PodcastHost')
    taxonomy_terms = models.ManyToManyField(Term, related_name='podcasts')
    dropbox_api = models.TextField(u'Dropbox API', null=True, blank=True)

    objects = query.PodcastQuerySet.as_manager()

    def __unicode__(self):
        return self.name

    def get_description_plain(self):
        from bs4 import BeautifulSoup

        return ' '.join(
            BeautifulSoup(
                self.description,
                'html.parser'
            ).findAll(text=True)
        ).strip()

    def get_previous_url(self, page, request):
        from django.utils.http import urlencode

        if page.has_previous():
            return '%s?%s' % (
                self.get_feed_body_url(request),
                urlencode(
                    {
                        'page': page.previous_page_number()
                    }
                )
            )

    def get_next_url(self, page, request):
        from django.utils.http import urlencode

        if page.has_next():
            return '%s?%s' % (
                self.get_feed_body_url(request),
                urlencode(
                    {
                        'page': page.next_page_number()
                    }
                )
            )

    def get_home_page_url(self, request):
        return request.build_absolute_uri('/')

    def get_feed_head_url(self, request):
        from django.core.urlresolvers import reverse

        return request.build_absolute_uri(
            reverse('podcast_feed_head')
        )

    def get_feed_body_url(self, request):
        from django.core.urlresolvers import reverse

        return request.build_absolute_uri(
            reverse('podcast_feed_body')
        )

    def get_rss_feed_url(self, request):
        from django.core.urlresolvers import reverse

        return request.build_absolute_uri(
            reverse('podcast_feed_rss')
        )

    def get_subscription_url(self, request):
        from django.core.urlresolvers import reverse

        return request.build_absolute_uri(
            reverse('podcast_subscribe')
        )

    def head_dict(self, request):
        artwork = {}

        if self.artwork:
            artwork = {
                '@1x': request.build_absolute_uri(self.artwork.url),
                '@2x': request.build_absolute_uri(self.artwork.url)
            }

        return {
            'version': settings.DOTPODCAST_VERSION,
            'title': self.name,
            'home_page_url': self.get_home_page_url(request),
            'meta_url': self.get_feed_head_url(request),
            'items_url': self.get_feed_body_url(request),
            'subscription_url': self.get_subscription_url(request),
            'description': self.subtitle,
            'user_comment': settings.USER_COMMENT,
            'author': self.author and self.author.as_dict(request) or None,
            'expired': False,
            'subtitle': self.subtitle,
            'taxonomy_terms': list(
                self.taxonomy_terms.values_list(
                    'url', flat=True
                )
            ),
            'artwork': artwork,
            'description_text': self.get_description_plain(),
            'description_html': self.description
        }

    def body_dict(self, request, page=1):
        from django.core.paginator import (
            Paginator, EmptyPage, PageNotAnInteger
        )

        episodes = self.episodes.select_related().prefetch_related().published()
        paginator = Paginator(
            episodes,
            settings.EPISODES_PER_PAGE
        )

        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        meta = {
            'version': settings.DOTPODCAST_VERSION,
            'total_count': episodes.count(),
            'per_page': settings.EPISODES_PER_PAGE
        }

        next_url = self.get_next_url(page_obj, request)
        if next_url:
            meta['next_url'] = next_url

        previous_url = self.get_previous_url(page_obj, request)
        if previous_url:
            meta['previous_url'] = previous_url

        return {
            'meta': meta,
            'items': [
                episode.as_dict(request)
                for episode in page_obj.object_list
            ]
        }

    def dump_head_json(self, stream, request):
        import json

        json.dump(
            self.head_dict(request),
            stream,
            ensure_ascii=False,
            indent=4
        )

    def dump_body_json(self, stream, request, page=1):
        import json

        json.dump(
            self.body_dict(request, page=page),
            stream,
            ensure_ascii=False,
            indent=4
        )

    def subscribe(
        self, kind, token,
        app_name='', app_url='', app_logo='',
        activity='listen'
    ):
        if kind == 'preview':
            for player in self.players.filter(app_url=app_url):
                return player

            player = self.players.create(
                app_name=app_name,
                app_url=app_url,
                app_logo=app_logo
            )

            player.full_clean()
            return player

        if kind == 'download':
            try:
                activity_kind = {
                    'listen': 'c',
                    'subscribe': 's',
                    '': None
                }[activity]
            except KeyError:
                raise ValidationError('Invalid activity.')

            for subscription in self.subscribers.filter(source_token=token):
                if activity_kind:
                    subscription.kind = activity_kind
                    subscription.full_clean()
                    subscription.save()

                return subscription

            subscriber = self.subscribers.create(
                app_name=app_name,
                app_url=app_url,
                app_logo=app_logo,
                source_token=token,
                kind=activity_kind or 'listen'
            )

            subscriber.full_clean()
            return subscriber

        if kind == 'transit':
            raise NotImplementedError('Transit tokens not yet implemented.')

    @transaction.atomic()
    def onboard(self, admin):
        self.author.user = admin
        self.author.save(update_fields=('user',))

        self.admins.add(admin)
        self.seasons.create(
            name=_('Season 1'),
            number=1
        )

    class Meta:
        ordering = ('name',)


class PodcastHost(models.Model):
    podcast = models.ForeignKey(
        Podcast,
        on_delete=models.CASCADE
    )

    host = models.ForeignKey(
        Host,
        related_name='podcasts',
        on_delete=models.CASCADE
    )

    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('host', 'podcast')


class Season(ContentObject):
    podcast = models.ForeignKey(
        Podcast,
        related_name='seasons',
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)
    number = models.PositiveIntegerField()

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = 'Season %d' % int(self.number)

        super(Season, self).save(*args, **kwargs)

    class Meta:
        ordering = ('number',)


class Episode(ContentObject):
    podcast = models.ForeignKey(
        Podcast,
        related_name='episodes',
        on_delete=models.CASCADE
    )

    guid = models.CharField(max_length=36)
    title = models.CharField(max_length=500)
    subtitle = models.TextField(null=True, blank=True)
    summary = models.TextField(null=True, blank=True)
    body = models.TextField(null=True, blank=True)
    kind = models.CharField(max_length=10,
        choices=(
            ('trailer', 'trailer'),
            ('episode', 'episode'),
            ('bonus', 'bonus')
        )
    )

    artwork = models.ImageField(
        max_length=124,
        upload_to=helpers.upload_episode_artwork,
        null=True,
        blank=True
    )

    banner_image = models.ImageField(
        upload_to=helpers.upload_banner,
        max_length=255, null=True, blank=True
    )

    date_published = models.DateTimeField()

    audio_enclosure = models.FileField(
        max_length=255, null=True, blank=True,
        upload_to=helpers.upload_episode_enclosure
    )

    audio_mimetype = models.CharField(max_length=50, null=True, blank=True)
    audio_duration = models.PositiveIntegerField(null=True, blank=True)
    audio_filesize = models.PositiveIntegerField(null=True, blank=True)

    video_enclosure = models.FileField(
        max_length=255, null=True, blank=True,
        upload_to=helpers.upload_episode_enclosure
    )

    video_mimetype = models.CharField(max_length=50, null=True, blank=True)
    video_duration = models.PositiveIntegerField(null=True, blank=True)
    video_filesize = models.PositiveIntegerField(null=True, blank=True)

    season = models.ForeignKey(
        Season,
        related_name='episodes',
        null=True,
        on_delete=models.SET_NULL
    )

    number = models.PositiveIntegerField(default=0)
    number_bonus = models.PositiveIntegerField(default=0)
    hosts = models.ManyToManyField(Host, through='EpisodeHost')
    taxonomy_terms = models.ManyToManyField(Term, related_name='episodes')
    tags = TaggableManager(blank=True)

    objects = query.EpisodeQuerySet.as_manager()

    def __unicode__(self):
        return self.title

    def download(self, request, kind):
        if kind == 'audio':
            url = request.build_absolute_uri(self.audio_enclosure.url)
            mime_type = self.audio_mimetype
            file_size = self.audio_filesize
        elif kind == 'video':
            url = request.build_absolute_uri(self.video_enclosure.url)
            mime_type = self.video_mimetype
            file_size = self.video_filesize
        else:
            raise Exception('Unknown media kind')

        return {
            'url': url,
            'mime_type': mime_type,
            'file_size': file_size
        }

    def save(self, *args, **kwargs):
        with transaction.atomic():
            if not self.guid:
                self.guid = unicode(uuid4())

            runtasks = []

            if not self.audio_duration:
                self.audio_duration = 0
                if self.audio_enclosure:
                    runtasks.append('set_audio_duration')

            if not self.audio_filesize:
                self.audio_filesize = 0
                if self.audio_enclosure:
                    runtasks.append('set_audio_filesize')

            if not self.video_duration:
                self.video_duration = 0
                if self.video_enclosure:
                    runtasks.append('set_video_duration')

            if not self.video_filesize:
                self.video_filesize = 0
                if self.video_enclosure:
                    runtasks.append('set_video_filesize')

            super(Episode, self).save(*args, **kwargs)

        for task in runtasks:
            func = getattr(tasks, task)
            django_rq.enqueue(func, self.pk)

    def get_page_url(self, request):
        from django.core.urlresolvers import reverse

        if self.number_bonus:
            url = reverse(
                'bonus_episode_detail',
                args=[
                    self.season.number,
                    unicode(self.number).zfill(2),
                    self.letter_bonus
                ]
            )
        else:
            url = reverse(
                'episode_detail',
                args=[
                    self.season.number,
                    unicode(self.number).zfill(2)
                ]
            )

        return request.build_absolute_uri(url)

    def get_body_plain(self):
        from bs4 import BeautifulSoup

        return ' '.join(
            BeautifulSoup(
                self.body,
                'html.parser'
            ).findAll(text=True)
        ).strip()

    def get_download_url(self, request, kind=None):
        from django.core.urlresolvers import reverse

        if not kind:
            if self.video_enclosure:
                kind = 'video'
            else:
                kind = 'audio'

        return request.build_absolute_uri(
            reverse(
                'episode_download',
                args=[kind]
            )
        )

    def get_filesize(self, kind=None):
        if not kind:
            if self.video_enclosure:
                kind = 'video'
            else:
                kind = 'audio'

        if kind == 'audio':
            return self.audio_filesize

        if kind == 'video':
            return self.video_filesize

        raise Exception('File type "%s" not recognised' % kind)

    def get_duration(self, kind=None):
        if not kind:
            if self.video_enclosure:
                kind = 'video'
            else:
                kind = 'audio'

        if kind == 'audio':
            return self.audio_duration

        if kind == 'video':
            return self.video_duration

        raise Exception('File type "%s" not recognised' % kind)

    def get_mimetype(self, kind=None):
        if not kind:
            if self.video_enclosure:
                kind = 'video'
            else:
                kind = 'audio'

        if kind == 'audio':
            return self.audio_mimetype

        if kind == 'video':
            return self.video_mimetype

        raise Exception('File type "%s" not recognised' % kind)

    def as_dict(self, request):
        data = {
            'id': self.guid,
            'url': self.get_page_url(request),
            'title': self.title,
            'content_text': self.get_body_plain(),
            'content_html': self.body,
            'summary': self.summary,
            'image': self.artwork and request.build_absolute_uri(
                self.artwork.url
            ),
            'date_published': self.date_published.replace(
                microsecond=0
            ).isoformat(),
            'author': self.podcast.author.as_dict(request)
        }

        if self.subtitle:
            data['subtitle'] = self.subtitle

        if self.season:
            data['season_number'] = self.season.number

        if self.number:
            data['episode_number'] = self.number

        if self.audio_enclosure:
            data['content_audio'] = {
                'mime_type': self.audio_mimetype,
                'duration': self.audio_duration,
                'url': self.get_download_url(request, 'audio'),
                'file_size': self.audio_filesize
            }

        if self.video_enclosure:
            data['content_video'] = {
                'mime_type': self.video_mimetype,
                'duration': self.video_duration,
                'url': self.get_download_url(request, 'video'),
                'file_size': self.video_filesize
            }

        if self.date_modified:
            data['date_modified'] = self.date_modified.replace(
                microsecond=0
            ).isoformat()

        return data

    @property
    def letter_bonus(self):
        if not self.number_bonus:
            return ''

        return string.lowercase[self.number_bonus - 1]

    class Meta:
        unique_together = ('number_bonus', 'number', 'kind', 'season')
        ordering = ('-date_published',)
        get_latest_by = 'date_published'


class EpisodeHost(models.Model):
    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE
    )

    host = models.ForeignKey(
        Host,
        related_name='hosted_episodes',
        on_delete=models.CASCADE
    )

    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('host', 'episode')


class EpisodeGuest(models.Model):
    episode = models.ForeignKey(
        Episode,
        on_delete=models.CASCADE
    )

    person = models.ForeignKey(
        Person,
        related_name='guesting_episodes',
        on_delete=models.CASCADE
    )

    ordering = models.PositiveIntegerField()

    class Meta:
        ordering = ('ordering',)
        unique_together = ('person', 'episode')


class Page(ContentObject):
    podcast = models.ForeignKey(
        Podcast,
        related_name='pages',
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=30, db_index=True)
    parent = models.ForeignKey('self', null=True)
    banner_image = models.ImageField(
        upload_to=helpers.upload_banner,
        max_length=255, null=True, blank=True
    )

    body = models.TextField(null=True, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    objects = query.PageQuerySet.as_manager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('page_detail', [self.slug])

    class Meta:
        unique_together = ('parent', 'slug')
        ordering = ('ordering',)


class BlogPost(ContentObject):
    podcast = models.ForeignKey(
        Podcast,
        related_name='blog_posts',
        on_delete=models.CASCADE
    )

    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=30, unique=True)
    date_published = models.DateTimeField(null=True, blank=True)

    banner_image = models.ImageField(
        upload_to=helpers.upload_banner,
        max_length=255, null=True, blank=True
    )

    body = models.TextField(null=True, blank=True)
    tags = TaggableManager(blank=True)
    objects = query.BlogPostQuerySet.as_manager()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('blog_post_detail', [self.slug])

    class Meta:
        ordering = ('-date_published',)
        get_latest_by = 'published'


class TokenPair(models.Model):
    public_token = models.CharField(max_length=64, unique=True)
    secret_token = models.CharField(max_length=256, unique=True)

    def save(self, *args, **kwargs):
        if not self.public_token:
            self.public_token = helpers.create_token(32)

        if not self.secret_token:
            self.secret_token = helpers.create_token(128, True)

        super(TokenPair, self).save(*args, **kwargs)


class Subscriber(TokenPair):
    podcast = models.ForeignKey(Podcast, related_name='subscribers')
    app_name = models.CharField(max_length=100, null=True, blank=True)
    app_url = models.URLField(u'app URL', max_length=512, null=True, blank=True)
    app_logo = models.URLField(max_length=512, null=True, blank=True)
    kind = models.CharField(max_length=1,
        choices=(
            ('c', 'casual listener'),
            ('s', 'subscriber')
        )
    )

    source_token = models.CharField(max_length=255)
    date_subscribed = models.DateTimeField(auto_now_add=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name or self.public_token

    def as_dict(self):
        return {
            'subscriber_token': self.public_token,
            'subscriber_secret': self.secret_token
        }

    class Meta:
        ordering = ('-last_fetched', '-date_subscribed')
        unique_together = ('source_token', 'podcast')


class Player(TokenPair):
    podcast = models.ForeignKey(Podcast, related_name='players')
    app_name = models.CharField(max_length=100, null=True, blank=True)
    app_url = models.URLField(u'app URL', max_length=512)
    app_logo = models.URLField(max_length=512, null=True, blank=True)
    last_fetched = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return self.name or self.app_url

    def as_dict(self):
        return {
            'preview_token': self.public_token,
            'preview_secret': self.secret_token
        }

    class Meta:
        ordering = ('-last_fetched',)
        unique_together = ('app_url', 'podcast')
