from django.http.response import HttpResponseRedirect
from django.views.generic import FormView
from .forms import OnboardingForm


class OnboardingFormView(FormView):
    form_class = OnboardingForm
    template_name = 'onboarding/form.html'
    success_url = '/admin/'

    def form_valid(self, form):
        form.save()
        return HttpResponseRedirect(
            self.get_success_url()
        )
