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

    activity = forms.ChoiceField(
        choices=(
            ('listen', 'listen'),
            ('subscribe', 'subscribe')
        ),
        initial='listen'
    )

    subscriber_hash = forms.CharField(required=False)

    def clean(self):
        app_url = self.cleaned_data.get('app_url')
        subscriber_hash = self.cleaned_data.get('subscriber_hash')
        token_kind = self.cleaned_data['token_kind']

        if token_kind == 'download' and not subscriber_hash:
            raise forms.ValidationError(
                'subscriber_hash is required to obtain a download token'
            )

        if token_kind == 'preview' and not app_url:
            raise forms.ValidationError(
                'app_url is required to obtain a preview token'
            )

        return self.cleaned_data

    def subscribe(self, podcast):
        self.instance = podcast.subscribe(
            kind=self.cleaned_data['token_kind'],
            token=self.cleaned_data['subscriber_hash'],
            app_name=self.cleaned_data.get('app_name'),
            app_url=self.cleaned_data.get('app_url'),
            app_logo=self.cleaned_data.get('app_logo'),
            activity=self.cleaned_data.get('activity')
        )

        return self.instance


class DownloadForm(forms.Form):
    iss = forms.CharField()
    iat = forms.IntegerField()
    exp = forms.IntegerField()
    aud = forms.CharField()
    sub = forms.CharField()
    content_id = forms.CharField()

    def download(self, podcast, kind, request):
        from urlparse import urlparse

        content_id = self.cleaned_data['content_id']
        for episode in podcast.episodes.filter(guid=content_id):
            self.instance = episode.download(request, kind)
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
