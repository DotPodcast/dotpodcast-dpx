from django.views.generic import FormView
from .forms import OnboardingForm


class OnboardingFormView(FormView):
    form_class = OnboardingForm
    template_name = 'onboarding/form.html'
