from django import forms
from django.utils.timezone import now
from django.utils.translation import ugettext as _
from ...core.widgets import DateTimeWidget
from ..models import Page


class PageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.fields['parent'].required = False

        if self.instance and self.instance.pk:
            self.fields['parent'].queryset = (
                self.fields['parent'].queryset.exclude(
                    pk=self.instance.pk
                )
            )

        self.fields['parent'].widget.choices = list(
            self.fields['parent'].queryset.choices()
        )

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
        model = Page
        fields = (
            'title',
            'slug',
            'body',
            'parent',
            'banner_image'
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
            'body': forms.Textarea(
                attrs={
                    'data-type': 'wysiwyg'
                }
            )
        }
