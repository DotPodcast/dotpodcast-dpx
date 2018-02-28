from django.conf import settings
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from ..hosting.models import Podcast


class OnboardingMiddlewareViewTestCase(TestCase):
    "Onboarding middleware tests"

    def test_get_no_podcast(self):
        """
        Test that the user is redirected to the onboarding form when
        visiting any URL other than one beginning with /onboarding/, if
        no podcast has been created.
        """

        client = Client()
        response = client.get('/foo/')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('onboarding_welcome'))

    def test_get_no_podcast_onboarding(self):
        """
        Test that the onboarding form is displayed correctly when there
        are no podcasts (ie: test that the browser doesn't enter a redirect
        loop)
        """

        client = Client()
        response = client.get(reverse('onboarding_welcome'))
        self.assertEqual(response.status_code, 200)

    def test_get_podcast(self):
        """
        Test that the user is able to see the requested URL once a podcast
        has been created
        """

        podcast = Podcast.objects.create(name='Test')

        try:
            client = Client()
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
        finally:
            podcast.delete()
