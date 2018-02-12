from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from ...core.widgets import DateTimeWidget
from ..models import Podcast, Episode


class EpisodeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})

        if not 'date_published' in initial:
            initial['date_published'] = now()

        super(EpisodeForm, self).__init__(*args, **kwargs)
        self.fields['body'].label = _('Show notes')
        self.fields['audio_enclosure'].required = True

        if self.instance and self.instance.pk:
            self.fields['audio_enclosure'].widget.attrs['data-template'] = 'button'

    # def clean(self):
    #     audio_enclosure = self.cleaned_data.get('audio_enclosure')
    #     video_enclosure = self.cleaned_data.get('video_enclosure')
    #
    #     if not audio_enclosure and not video_enclosure:
    #         raise forms.ValidationError(
    #             _('Supply either an audio or video enclosure.')
    #         )
    #
    #     return self.cleaned_data

    def save(self, commit=True):
        obj = super(EpisodeForm, self).save(commit=False)
        for podcast in Podcast.objects.all()[:1]:
            obj.podcast = podcast

        if commit:
            obj.save()

        return obj

    @property
    def header_fields(self):
        return [
            field for field in self
            if field.name in ('title', 'subtitle')
        ]

    @property
    def file_fields(self):
        return [
            field for field in self
            if field.name in (
                'audio_enclosure',
                # 'video_enclosure',
                'artwork',
                'banner_image'
            )
        ]

    @property
    def other_fields(self):
        return [
            field for field in self
            if field.name not in ('title', 'subtitle')
            and not field.name.endswith('_enclosure')
        ]

    class Meta:
        model = Episode
        fields = (
            'audio_enclosure',
            # 'video_enclosure',
            'title',
            'subtitle',
            'date_published',
            'summary',
            'body',
            'artwork',
            'banner_image',
            'season',
            'number',
            'tags'
        )

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'input-lg'
                }
            ),
            'subtitle': forms.TextInput(
                attrs={
                    'class': 'input-sm'
                }
            ),
            'artwork': forms.ClearableFileInput(
                attrs={
                    'accept': 'image/*'
                }
            ),
            'banner_image': forms.ClearableFileInput(
                attrs={
                    'accept': 'image/*'
                }
            ),
            'audio_enclosure': forms.ClearableFileInput(
                attrs={
                    'accept': 'audio/*',
                    'data-template': 'dropzone'
                }
            ),
            # 'video_enclosure': forms.FileInput(
            #     attrs={
            #         'accept': 'video/*'
            #     }
            # ),
            'date_published': DateTimeWidget(
                options={
                    'todayBtn': 'true'
                },
                usel10n=True,
                bootstrap_version=3
            ),
            'summary': forms.Textarea(
                attrs={
                    'rows': 3
                }
            ),
            'body': forms.Textarea(
                attrs={
                    'data-type': 'wysiwyg'
                }
            )
        }
