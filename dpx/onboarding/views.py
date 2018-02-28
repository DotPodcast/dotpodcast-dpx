from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http.response import HttpResponseRedirect
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView, View
from dropbox import DropboxOAuth2Flow
from .forms import OnboardingForm
from ..hosting.models import Podcast


class OnboardingFormView(FormView):
    form_class = OnboardingForm
    template_name = 'onboarding/form.html'
    success_url = '/admin/'

    def get(self, request):
        if Podcast.objects.exists():
            messages.warning(
                request,
                _('A podcast has already been setup.')
            )

            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)

        return super(OnboardingFormView, self).get(request)

    def form_valid(self, form):
        form.save()

        return HttpResponseRedirect(
            reverse('onboarding_callback')
        )


class OnboardingCallbackView(LoginRequiredMixin, View):
    @transaction.atomic()
    def get(self, request):
        podcast = Podcast.objects.first()
        if podcast is None:
            return HttpResponseRedirect(
                reverse('onboarding_welcome')
            )

        podcast.onboard(request.user)

        messages.success(
            self.request,
            _('Hi %s. Your podcast has been setup.') % (
                request.user.first_name or request.user.username
            )
        )

        return HttpResponseRedirect(
            self.get_success_url()
        )

    def get_success_url(self):
        return (
            self.request.GET.get('next') or
            settings.LOGIN_REDIRECT_URL
        )

        return '%s?%s' % (
            reverse('dropbox_setup'),
            {
                'next': (
                    self.request.GET.get('next') or
                    settings.LOGIN_REDIRECT_URL
                )
            }
        )


class DropboxSetupView(View):
    def get(self, request):
        flow = DropboxOAuth2Flow(
            settings.DROPBOX_API_KEY,
            settings.DROPBOX_API_SECRET,
            request.build_absolute_uri(
                '%s?%s' % (
                    reverse('dropbox_callback'),
                    urlencode(
                        {
                            'next': (
                                self.request.GET.get('next') or
                                settings.LOGIN_REDIRECT_URL
                            )
                        }
                    )
                )
            ),
            request.session,
            'csrfmiddlewaretoken'
        )

        return HttpResponseRedirect(
            flow.start()
        )


class DropboxCompleteView(View):
    pass
