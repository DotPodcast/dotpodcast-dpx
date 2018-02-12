from django.conf.urls import url
from .views import *


urlpatterns = [
    url(
        r'^$',
        OnboardingFormView.as_view(),
        name='onboarding_welcome'
    ),
    url(
        r'^dropbox/$',
        DropboxSetupView.as_view(),
        name='dropbox_setup'
    ),
    url(
        r'^dropbox/callback/$',
        DropboxCompleteView.as_view(),
        name='dropbox_callback'
    ),
    url(
        r'^complete/$',
        OnboardingCallbackView.as_view(),
        name='onboarding_callback'
    )
]
