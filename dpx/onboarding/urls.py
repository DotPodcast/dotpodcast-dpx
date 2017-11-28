from django.conf.urls import url
from .views import OnboardingFormView


urlpatterns = [
    url(r'^$', OnboardingFormView.as_view(), name='onboarding_welcome'),
]
