from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from ...core.widgets import DateTimeWidget
from ..models import Podcast, BlogPost


class BlogPostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        initial = kwargs.get('initial', {})
        if not 'date_published' in initial:
            initial['date_published'] = now()

        super(BlogPostForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super(BlogPostForm, self).save(commit=False)
        for podcast in Podcast.objects.all()[:1]:
            obj.podcast = podcast

        if commit:
            obj.save()

        return obj

    @property
    def header_fields(self):
        return [
            field for field in self
            if field.name in ('title',)
        ]

    @property
    def file_fields(self):
        return [
            self['banner_image']
        ]

    @property
    def other_fields(self):
        return [
            field for field in self
            if field.name not in ('title', 'banner_image')
        ]

    class Meta:
        model = BlogPost
        fields = (
            'title',
            'slug',
            'date_published',
            'body',
            'banner_image',
            'tags'
        )

        widgets = {
            'title': forms.TextInput(
                attrs={
                    'class': 'input-lg'
                }
            ),
            'slug': forms.TextInput(
                attrs={
                    'data-slugify': 'title'
                }
            ),
            'date_published': DateTimeWidget(
                options={
                    'todayBtn': 'true'
                },
                usel10n=True,
                bootstrap_version=3
            ),
            'body': forms.Textarea(
                attrs={
                    'data-type': 'wysiwyg'
                }
            )
        }
