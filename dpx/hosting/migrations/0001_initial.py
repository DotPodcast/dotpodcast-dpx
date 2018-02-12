# -*- coding: utf-8 -*-
# Generated by Django 1.11.8 on 2017-12-21 20:51
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import dpx.hosting.helpers
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BlogPost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[(b'a', b'active'), (b't', b'trashed')], default=b'a', editable=False, max_length=1)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=30, unique=True)),
                ('date_published', models.DateTimeField(blank=True, null=True)),
                ('banner_image', models.ImageField(blank=True, max_length=255, null=True, upload_to=dpx.hosting.helpers.upload_banner)),
                ('body', models.TextField(blank=True, null=True)),
            ],
            options={
                'ordering': ('-date_published',),
                'get_latest_by': 'published',
            },
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[(b'a', b'active'), (b't', b'trashed')], default=b'a', editable=False, max_length=1)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(max_length=500)),
                ('subtitle', models.TextField(blank=True, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('body', models.TextField(blank=True, null=True)),
                ('artwork', models.ImageField(blank=True, max_length=124, null=True, upload_to=dpx.hosting.helpers.upload_episode_artwork)),
                ('banner_image', models.ImageField(blank=True, max_length=255, null=True, upload_to=dpx.hosting.helpers.upload_banner)),
                ('date_published', models.DateTimeField()),
                ('audio_enclosure', models.FileField(blank=True, max_length=255, null=True, upload_to=dpx.hosting.helpers.upload_episode_enclosure)),
                ('audio_mimetype', models.CharField(blank=True, max_length=50, null=True)),
                ('audio_duration', models.PositiveIntegerField()),
                ('audio_filesize', models.PositiveIntegerField()),
                ('video_enclosure', models.FileField(blank=True, max_length=255, null=True, upload_to=dpx.hosting.helpers.upload_episode_enclosure)),
                ('video_mimetype', models.CharField(blank=True, max_length=50, null=True)),
                ('video_duration', models.PositiveIntegerField()),
                ('video_filesize', models.PositiveIntegerField()),
                ('number', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('-date_published',),
                'get_latest_by': 'date_published',
            },
        ),
        migrations.CreateModel(
            name='EpisodeGuest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField()),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hosting.Episode')),
            ],
            options={
                'ordering': ('ordering',),
            },
        ),
        migrations.CreateModel(
            name='EpisodeHost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField()),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hosting.Episode')),
            ],
            options={
                'ordering': ('ordering',),
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[(b'a', b'active'), (b't', b'trashed')], default=b'a', editable=False, max_length=1)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('title', models.CharField(max_length=50)),
                ('slug', models.SlugField(max_length=30)),
                ('banner_image', models.ImageField(blank=True, max_length=255, null=True, upload_to=dpx.hosting.helpers.upload_banner)),
                ('body', models.TextField(blank=True, null=True)),
                ('ordering', models.PositiveIntegerField(default=0)),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='hosting.Page')),
            ],
            options={
                'ordering': ('ordering',),
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[(b'a', b'active'), (b't', b'trashed')], default=b'a', editable=False, max_length=1)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('slug', models.CharField(max_length=36, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('url', models.URLField(blank=True, max_length=500, null=True, verbose_name=b'URL')),
                ('avatar', models.ImageField(blank=True, max_length=64, null=True, upload_to=dpx.hosting.helpers.upload_avatar)),
                ('public_key', models.CharField(blank=True, db_index=True, max_length=500, null=True)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Podcast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[(b'a', b'active'), (b't', b'trashed')], default=b'a', editable=False, max_length=1)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=300)),
                ('subtitle', models.TextField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('artwork', models.ImageField(blank=True, max_length=255, null=True, upload_to=dpx.hosting.helpers.upload_podcast_artwork)),
                ('banner_image', models.ImageField(blank=True, max_length=255, null=True, upload_to=dpx.hosting.helpers.upload_banner)),
                ('publisher_name', models.CharField(max_length=300)),
                ('publisher_url', models.URLField(blank=True, max_length=500, null=True, verbose_name=b'publisher URL')),
                ('publisher_logo', models.URLField(blank=True, max_length=500, null=True)),
                ('dropbox_api', models.TextField(blank=True, null=True, verbose_name='Dropbox API')),
                ('admins', models.ManyToManyField(related_name='publishers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='PodcastHost',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ordering', models.PositiveIntegerField()),
                ('podcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='hosting.Podcast')),
            ],
            options={
                'ordering': ('ordering',),
            },
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(choices=[(b'a', b'active'), (b't', b'trashed')], default=b'a', editable=False, max_length=1)),
                ('date_modified', models.DateTimeField(auto_now=True, null=True)),
                ('name', models.CharField(max_length=100)),
                ('number', models.PositiveIntegerField()),
                ('podcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasons', to='hosting.Podcast')),
            ],
            options={
                'ordering': ('number',),
            },
        ),
        migrations.CreateModel(
            name='Subscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('source_token', models.CharField(max_length=255, unique=True)),
                ('public_token', models.CharField(max_length=32, unique=True)),
                ('secret_token', models.CharField(max_length=128, unique=True)),
                ('date_subscribed', models.DateTimeField(auto_now_add=True)),
                ('last_fetched', models.DateTimeField(blank=True, null=True)),
                ('podcast', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscribers', to='hosting.Podcast')),
            ],
            options={
                'ordering': ('-last_fetched', '-date_subscribed'),
            },
        ),
        migrations.CreateModel(
            name='Taxonomy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('url', models.URLField(max_length=500, unique=True, verbose_name=b'URL')),
                ('description', models.TextField(blank=True, null=True)),
                ('required', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300)),
                ('url', models.URLField(max_length=500, unique=True, verbose_name=b'URL')),
                ('description', models.TextField(blank=True, null=True)),
                ('taxonomy', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terms', to='hosting.Taxonomy')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Author',
            fields=[
                ('person_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='hosting.Person')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('hosting.person',),
        ),
        migrations.CreateModel(
            name='Host',
            fields=[
                ('person_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='hosting.Person')),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='host', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
            bases=('hosting.person',),
        ),
        migrations.AddField(
            model_name='podcast',
            name='taxonomy_terms',
            field=models.ManyToManyField(related_name='podcasts', to='hosting.Term'),
        ),
        migrations.AddField(
            model_name='episodeguest',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guesting_episodes', to='hosting.Person'),
        ),
        migrations.AddField(
            model_name='episode',
            name='podcast',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='hosting.Podcast'),
        ),
        migrations.AddField(
            model_name='episode',
            name='season',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='episodes', to='hosting.Season'),
        ),
        migrations.AddField(
            model_name='episode',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='episode',
            name='taxonomy_terms',
            field=models.ManyToManyField(related_name='episodes', to='hosting.Term'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='podcast',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blog_posts', to='hosting.Podcast'),
        ),
        migrations.AddField(
            model_name='blogpost',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='podcasthost',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='podcasts', to='hosting.Host'),
        ),
        migrations.AddField(
            model_name='podcast',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='podcasts', to='hosting.Author'),
        ),
        migrations.AddField(
            model_name='podcast',
            name='hosts',
            field=models.ManyToManyField(through='hosting.PodcastHost', to='hosting.Host'),
        ),
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set([('parent', 'slug')]),
        ),
        migrations.AddField(
            model_name='episodehost',
            name='host',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hosted_episodes', to='hosting.Host'),
        ),
        migrations.AlterUniqueTogether(
            name='episodeguest',
            unique_together=set([('person', 'episode')]),
        ),
        migrations.AddField(
            model_name='episode',
            name='hosts',
            field=models.ManyToManyField(through='hosting.EpisodeHost', to='hosting.Host'),
        ),
        migrations.AlterUniqueTogether(
            name='podcasthost',
            unique_together=set([('host', 'podcast')]),
        ),
        migrations.AlterUniqueTogether(
            name='episodehost',
            unique_together=set([('host', 'episode')]),
        ),
        migrations.AlterUniqueTogether(
            name='episode',
            unique_together=set([('number', 'season')]),
        ),
    ]
