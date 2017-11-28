from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django.utils.translation import ugettext_lazy as _
from ..hosting.models import Podcast, Author


class OnboardingForm(forms.Form):
    podcast_name = forms.CharField(
        label=_('Podcast name'),
        widget=forms.TextInput(
            attrs={
                'placeholder': _('My new podcast')
            }
        )
    )

    admin_username = forms.RegexField(
        label=_('Admin username'),
        regex=r'^[a-z0-9]+$',
        help_text=_('Use lowercase letters and numbers'),
        initial='admin'
    )

    admin_password = forms.CharField(
        label=_('Admin account password'),
        widget=forms.PasswordInput()
    )

    admin_password_confirm = forms.CharField(
        label=_('Confirm your password'),
        widget=forms.PasswordInput()
    )

    language = forms.ChoiceField(
        choices=settings.LANGUAGES,
        initial=settings.LANGUAGE_CODE
    )

    def clean_admin_password_confirm(self):
        password = self.cleaned_data.get('admin_password')
        confirmation = self.cleaned_data.get('admin_password_confirm')

        if password != confirmation:
            raise forms.ValidationError(
                _('The password and confirmation do not match.')
            )

        return confirmation

    @transaction.atomic()
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['admin_username'],
            password=self.cleaned_data['admin_password']
        )

        author = Author.objects.create(
            user=user,
            slug=user.username,
            name=user.username
        )

        podcast = Podcast.objects.create(
            name=self.cleaned_data['podcast_name'],
            author=author,
            publisher_name=user.username
        )

        podcast.admins.add(user)
        return podcast
