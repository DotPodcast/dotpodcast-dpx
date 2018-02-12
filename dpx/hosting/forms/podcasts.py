from django import forms
from ..models import Podcast, Episode


class SubscribeForm(forms.Form):
    app_name = forms.CharField(required=False)
    app_url = forms.URLField(required=False)
    app_logo = forms.URLField(required=False)
    token_kind = forms.ChoiceField(
        choices=(
            ('preview', 'preview'),
            ('download', 'download'),
            ('transit', 'transit')
        )
    )

    subscriber_hash = forms.CharField()

    def subscribe(self, podcast):
        self.instance = podcast.subscribe(
            kind=self.cleaned_data['token_kind'],
            token=self.cleaned_data['subscriber_hash'],
            app_name=self.cleaned_data.get('app_name'),
            app_url=self.cleaned_data.get('app_url'),
            app_logo=self.cleaned_data.get('app_logo')
        )

        return self.instance


class DownloadForm(forms.Form):
    iss = forms.CharField()
    iat = forms.IntegerField()
    exp = forms.IntegerField()
    aud = forms.CharField()
    sub = forms.CharField()
    content_id = forms.CharField()

    def download(self, podcast, kind):
        from urllib.parse import urlparse

        content_id = self.cleaned_data['content_id']
        path = urlparse(content_id).path
        start, podcast_slug, episode_slug, end = path.split('/')

        if podcast_slug == podcast.slug:
            for episode in podcast.episodes.filter(slug=episode_slug):
                self.instance = episode.download(kind)
                return self.instance

        raise Episode.NotFound('Episode not found.')


class PodcastForm(forms.ModelForm):
    class Meta:
        model = Podcast
        fields = (
            'name',
            'subtitle',
            'description',
            'artwork',
            'banner_image',
            'publisher_name',
            'publisher_url',
            'publisher_logo'
        )
