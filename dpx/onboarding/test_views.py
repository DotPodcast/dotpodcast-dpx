from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.contrib.messages import get_messages
from ..hosting.models import Podcast, Author
from .views import OnboardingFormView, OnboardingCallbackView


class OnboardingFormViewTestCase(TestCase):
    "Onboarding view tests"

    def test_get_no_podcast(self):
        """
        Test that the onboarding form is shown when no podcast has been setup.
        """

        client = Client()
        response = client.get(reverse('onboarding_welcome'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.template_name, ['onboarding/form.html'])

    def test_post(self):
        """
        Test that a podcast is created and readied for onboarding when a user
        fills in the initial form.
        """

        client = Client()
        response = client.post(
            reverse('onboarding_welcome'),
            {
                'podcast_name': 'Test',
                'author_name': 'Jon Doe',
                'language': 'en'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('onboarding_callback'))

        podcast = Podcast.objects.get()
        term = podcast.taxonomy_terms.get()

        self.assertEqual(podcast.name, 'Test')
        self.assertEqual(podcast.author.name, 'Jon Doe')
        self.assertEqual(term.name, 'English')
        self.assertEqual(
            term.url,
            'https://dotpodcast.co/taxonomies/language#en'
        )

    def test_get_podcast(self):
        """
        Test that the user is redirected to the login page if they have
        already setup a podcast.
        """

        podcast = Podcast.objects.create(name='Test')

        try:
            client = Client()
            response = client.get(reverse('onboarding_welcome'))
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, settings.LOGIN_REDIRECT_URL)
            self.assertIn('A podcast has already been setup.', messages)
        finally:
            podcast.delete()


class OnboardingCallbackView(TestCase):
    "Onboarding callback view tests"

    def test_get_anonymous(self):
        """
        Test that the user is redirected to login when accessing the
        onboarding-callback view.
        """

        client = Client()
        path = reverse('onboarding_callback')
        response = client.get(path)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            '%s?next=%s' % (settings.LOGIN_URL, path)
        )

    def test_get_authenticated_no_podcast(self):
        """
        Test that a logged-in user sees a 404 when directly visiting the
        onboarding-callback URL, if there is no podcast.
        """

        user = User.objects.create_user(
            'test',
            'test@example.com',
            'test'
        )

        try:
            client = Client()
            self.assertTrue(client.login(username='test', password='test'))
            response = client.get(reverse('onboarding_callback'))
            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('onboarding_welcome'))
        finally:
            user.delete()

    def test_get_authenticated_podcast(self):
        """
        Test that a logged-in user is redirected to the import page when
        the onboarding process is complete
        """

        user = User.objects.create_user(
            'test',
            'test@example.com',
            'test'
        )

        podcast = Podcast.objects.create(
            name='Test',
            author=Author.objects.create(
                name='Test'
            )
        )

        try:
            client = Client()
            self.assertTrue(client.login(username='test', password='test'))
            response = client.get(reverse('onboarding_callback'))
            messages = [m.message for m in get_messages(response.wsgi_request)]

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.url, reverse('admin_import_start'))
            self.assertIn('Hi test. Your podcast has been setup.', messages)
        finally:
            user.delete()
            podcast.delete()
