from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
from django.utils.timezone import now
from django.core.files import File
from os import path
from ..models import Podcast, Author, Taxonomy
from ..views.admin.dashboard import DashboardView
from ..views.admin.episodes import *
from ..views.admin.blog import *
from ..views.admin.pages import *
from ..views.admin.importing import CreateImportView, ImportDetailView
from .. import ADMIN_MENU_ITEMS


class PodcastMixin(object):
    urlname = ''
    urlargs = []
    view = None

    def setUp(self):
        self.user = User.objects.create_user('test', 'test@example.com', 'test')
        self.podcast = Podcast.objects.create(
            name='Test',
            author=Author.objects.create(
                user=self.user,
                name='Test'
            )
        )

        self.podcast.seasons.create(
            number=1,
            name='Season 1'
        )

        self.podcast.taxonomy_terms.add(
            Taxonomy.objects.create(
                name='Language',
                url='https://dotpodcast.co/taxonomies/language',
                description='The spoken language of the podcast',
                required=True
            ).terms.create(
                name='English',
                url='https://dotpodcast.co/taxonomies/language#en'
            )
        )

    def test_get_anonymous(self):
        """
        Test that an anonymous user is redirected to the login page.
        """
        path = reverse(self.urlname, args=self.urlargs)
        response = self.client.get(path)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            '%s?next=%s' % (settings.LOGIN_URL, path)
        )

    def test_get_authenticated(self):
        """
        Test that the correct template is rendered, the right menu item is
        selected and the content can be accessed as a logged-in user.
        """

        self.client.login(username='test', password='test')
        path = reverse(self.urlname, args=self.urlargs)
        response = self.client.get(path)
        menu_items = list(response.context['menu_items']())

        self.assertEqual(response.status_code, 200)
        self.assertIn(self.view.template_name, response.template_name)

        if self.view.menu_item_name:
            menu_item_url = None
            for (item_name, item_title, urlname) in ADMIN_MENU_ITEMS:
                if item_name == self.view.menu_item_name:
                    menu_item_url = reverse('admin_%s' % urlname)
                    break

            found = False
            for item in menu_items:
                if menu_item_url and item['url'] == menu_item_url:
                    self.assertTrue(item['selected'])
                    found = True
                else:
                    self.assertFalse(item['selected'])

            if not found:
                self.fail('No selected menu item found')

        if hasattr(self.view, 'form_class'):
            form = response.context['form']
            self.assertIsInstance(form, self.view.form_class)

    def _test_post(self, data, checks, get_success_url):
        self.client.login(username='test', password='test')
        path = reverse(self.urlname, args=self.urlargs)
        response = self.client.post(path, data)

        if response.status_code == 200:
            for error in response.context['form'].errors:
                self.fail(error)

        self.assertEqual(response.status_code, 302)
        obj = self.view.model.objects.order_by('-pk')[0]
        for key, value in checks.items():
            if callable(value):
                self.assertTrue(value(obj))
            else:
                self.assertEqual(getattr(obj, key), value)

        self.assertEqual(response.url, get_success_url(obj))

    def tearDown(self):
        self.user.delete()
        self.podcast.delete()
        Taxonomy.objects.all().delete()


class DashboardViewTest(PodcastMixin, TestCase):
    view = DashboardView
    urlname = 'admin_dashboard'


class EpisodeListViewTestCase(PodcastMixin, TestCase):
    view = EpisodeListView
    urlname = 'admin_episode_list'


class CreateEpisodeFormViewTestCase(PodcastMixin, TestCase):
    view = CreateEpisodeFormView
    urlname = 'admin_create_episode'

    def test_post(self):
        self._test_post(
            {
                'title': 'Test',
                'season': self.podcast.seasons.get().pk,
                'number': 1,
                'date_published': now().strftime('%Y-%m-%d %H:%I:%S'),
                'audio_enclosure': open(
                    path.join(
                        path.dirname(__file__),
                        '..',
                        'fixtures',
                        'test_enclosure.mp3'
                    ),
                    'rb'
                )
            },
            {
                'title': 'Test',
                'season': lambda o: o.season.number == 1,
                'number': 1
            },
            lambda o: reverse('admin_update_episode', args=[o.pk])
        )


class UpdateEpisodeFormViewTestCase(PodcastMixin, TestCase):
    view = UpdateEpisodeFormView
    urlname = 'admin_update_episode'

    def setUp(self):
        super(UpdateEpisodeFormViewTestCase, self).setUp()
        self.episode = self.podcast.episodes.create(
            title='Test',
            season=self.podcast.seasons.get(),
            number=1,
            date_published=now(),
            audio_enclosure=File(
                open(
                    path.join(
                        path.dirname(__file__),
                        '..',
                        'fixtures',
                        'test_enclosure.mp3'
                    ),
                    'rb'
                )
            )
        )

        self.urlargs = [self.episode.pk]

    def test_post(self):
        self._test_post(
            {
                'title': 'Test',
                'season': self.podcast.seasons.get().pk,
                'number': 1,
                'date_published': now().strftime('%Y-%m-%d %H:%I:%S')
            },
            {
                'title': 'Test',
                'season': lambda o: o.season.number == 1,
                'number': 1
            },
            lambda o: reverse('admin_update_episode', args=[self.episode.pk])
        )

    def tearDown(self):
        self.episode.delete()


class DeleteEpisodeViewTestCase(PodcastMixin, TestCase):
    view = DeleteEpisodeView
    urlname = 'admin_delete_episode'

    def setUp(self):
        super(DeleteEpisodeViewTestCase, self).setUp()
        self.episode = self.podcast.episodes.create(
            title='Test',
            season=self.podcast.seasons.get(),
            number=1,
            date_published=now(),
            audio_enclosure=File(
                open(
                    path.join(
                        path.dirname(__file__),
                        '..',
                        'fixtures',
                        'test_enclosure.mp3'
                    ),
                    'rb'
                )
            )
        )

        self.urlargs = [self.episode.pk]

    def test_post(self):
        self.client.login(username='test', password='test')

        path = reverse(self.urlname, args=self.urlargs)
        response = self.client.post(path)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            self.view.model.objects.filter(
                pk=self.episode.pk
            ).exists()
        )

        self.assertEqual(response.url, reverse('admin_episode_list'))


class BlogPostListViewTestCase(PodcastMixin, TestCase):
    view = BlogPostListView
    urlname = 'admin_blog_post_list'


class CreateBlogPostFormViewTestCase(PodcastMixin, TestCase):
    view = CreateBlogPostFormView
    urlname = 'admin_create_blog_post'

    def test_post(self):
        self._test_post(
            {
                'title': 'Test',
                'slug': 'test',
                'date_published': now().strftime('%Y-%m-%d %H:%I:%S')
            },
            {
                'title': 'Test'
            },
            lambda o: reverse('admin_update_blog_post', args=[o.pk])
        )


class UpdateBlogPostFormViewTestCase(PodcastMixin, TestCase):
    view = UpdateBlogPostFormView
    urlname = 'admin_update_blog_post'

    def setUp(self):
        super(UpdateBlogPostFormViewTestCase, self).setUp()
        self.post = self.podcast.blog_posts.create(
            title='Test',
            slug='test',
            date_published=now()
        )

        self.urlargs = [self.post.pk]

    def test_post(self):
        self._test_post(
            {
                'title': 'Test',
                'slug': 'test',
                'date_published': now().strftime('%Y-%m-%d %H:%I:%S')
            },
            {
                'title': 'Test'
            },
            lambda o: reverse('admin_update_blog_post', args=[self.post.pk])
        )

    def tearDown(self):
        self.post.delete()


class DeleteBlogPostViewTestCase(PodcastMixin, TestCase):
    view = DeleteBlogPostView
    urlname = 'admin_delete_blog_post'

    def setUp(self):
        super(DeleteBlogPostViewTestCase, self).setUp()
        self.post = self.podcast.blog_posts.create(
            title='Test',
            slug='test',
            date_published=now()
        )

        self.urlargs = [self.post.pk]

    def test_post(self):
        self.client.login(username='test', password='test')

        path = reverse(self.urlname, args=self.urlargs)
        response = self.client.post(path)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            self.view.model.objects.filter(
                pk=self.post.pk
            ).exists()
        )

        self.assertEqual(response.url, reverse('admin_blog_post_list'))


class PageListViewTestCase(PodcastMixin, TestCase):
    view = PageListView
    urlname = 'admin_page_list'


class CreatePageFormViewTestCase(PodcastMixin, TestCase):
    view = CreatePageFormView
    urlname = 'admin_create_page'

    def test_post(self):
        self._test_post(
            {
                'title': 'Test',
                'slug': 'test',
                'body': 'Foo bar'
            },
            {
                'title': 'Test'
            },
            lambda o: reverse('admin_update_page', args=[o.pk])
        )


class UpdatePageFormViewTestCase(PodcastMixin, TestCase):
    view = UpdatePageFormView
    urlname = 'admin_update_page'

    def setUp(self):
        super(UpdatePageFormViewTestCase, self).setUp()
        self.page = self.podcast.pages.create(
            title='Test',
            slug='test'
        )

        self.urlargs = [self.page.pk]

    def test_post(self):
        self._test_post(
            {
                'title': 'Test',
                'slug': 'test'
            },
            {
                'title': 'Test'
            },
            lambda o: reverse('admin_update_page', args=[self.page.pk])
        )

    def tearDown(self):
        self.page.delete()


class DeletePageViewTestCase(PodcastMixin, TestCase):
    view = DeletePageView
    urlname = 'admin_delete_page'

    def setUp(self):
        super(DeletePageViewTestCase, self).setUp()
        self.page = self.podcast.pages.create(
            title='Test',
            slug='test'
        )

        self.urlargs = [self.page.pk]

    def test_post(self):
        self.client.login(username='test', password='test')

        path = reverse(self.urlname, args=self.urlargs)
        response = self.client.post(path)

        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            self.view.model.objects.filter(
                pk=self.page.pk
            ).exists()
        )

        self.assertEqual(response.url, reverse('admin_page_list'))


class CreateImportViewTestCase(PodcastMixin, TestCase):
    view = CreateImportView
    urlname = 'admin_import_start'

    def test_post(self):
        self.client.login(username='test', password='test')
        path = reverse(self.urlname)
        response = self.client.post(
            path,
            {
                'url': 'http://example.com/rss.xml'
            }
        )

        if response.status_code == 200:
            for error in response.context['form'].errors:
                self.fail(error)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin_import_progress'))


class ImportDetailViewTestCase(PodcastMixin, TestCase):
    view = ImportDetailView
    urlname = 'admin_import_progress'
