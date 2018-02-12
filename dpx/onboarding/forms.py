from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from ..hosting import TAXONOMIES
from ..hosting.models import Podcast, Author, Taxonomy


class OnboardingForm(forms.Form):
    podcast_name = forms.CharField(
        label=_('Podcast name'),
        widget=forms.TextInput(
            attrs={
                'placeholder': _('My new podcast')
            }
        )
    )

    author_name = forms.CharField()

    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        initial=settings.LANGUAGE_CODE
    )

    @transaction.atomic()
    def save(self, commit=True):
        author = Author.objects.create(
            name=self.cleaned_data['author_name']
        )

        podcast = Podcast(
            name=self.cleaned_data['podcast_name'],
            author=author,
            publisher_name=self.cleaned_data['author_name']
        )

        if commit:
            podcast.save()

        return podcast

    def _save_m2m(self):
        taxonomy = TAXONOMIES['language']
        taxonomy = Taxonomy.objects.create(
            name=taxonomy['name'],
            url=taxonomy['base_url'],
            description=taxonomy['description'],
            required=True
        )

        language = self.cleaned_data.get('language')
        for (key, name) in settings.LANGUAGES:
            if key == language:
                term = taxonomy.terms.create(
                    name=name,
                    url=taxonomy['url_template'] % key
                )

                self.instance.terms.add(term)
                break

        return term
