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
    def save(self):
        author = Author.objects.create(
            name=self.cleaned_data['author_name']
        )

        podcast = Podcast(
            name=self.cleaned_data['podcast_name'],
            author=author,
            publisher_name=self.cleaned_data['author_name']
        )

        podcast.save()
        self.instance = podcast

        taxonomy = TAXONOMIES['language']
        language = self.cleaned_data.get('language')

        for (key, name) in settings.LANGUAGES:
            if key == language:
                term = Taxonomy.objects.create(
                    name=taxonomy['name'],
                    url=taxonomy['base_url'],
                    description=taxonomy['description'],
                    required=True
                ).terms.create(
                    name=name,
                    url=taxonomy['term_template'] % key
                )

                podcast.taxonomy_terms.add(term)
                break

        return podcast
