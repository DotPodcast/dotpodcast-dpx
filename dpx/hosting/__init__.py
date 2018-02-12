from django.utils.translation import ugettext_lazy as _


ADMIN_MENU_ITEMS = [
    ('dashboard', 'Home', 'dashboard'),
    ('episodes', 'Episodes', 'episode_list'),
    ('pages', 'Pages', 'page_list'),
    ('blog_posts', 'Blog', 'blog_post_list'),
    ('analytics', 'Analytics', 'analytics'),
    ('settings', 'Settings', 'podcast_settings')
]

TAXONOMIES = {
    'language': {
        'name': _('Language'),
        'base_url': 'https://dotpodcast.co/taxonomies/language',
        'term_template': 'https://dotpodcast.co/taxonomies/language#%s',
        'description': _('The spoken language of the podcast')
    }
}
