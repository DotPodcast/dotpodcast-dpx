from . import ImporterBase
from .xml import XmlMixin
from bs4 import BeautifulSoup


class RssImporter(XmlMixin, ImporterBase):
    verbose_name = 'RSS'

    def apply(self, data):
        root = BeautifulSoup(data, 'lxml')
        if root is not None:
            actual_item_count = data.count('</item>')
            found_item_count = len(root.findAll('item'))

            if found_item_count == actual_item_count:
                channel = self.get_first_tag(root, 'channel', False)
                if channel is not False:
                    return root

    def get_podcast_data(self, root):
        channel = self.get_first_tag(root, 'channel')
        image = self.get_first_tag(channel, 'itunes:image', False)
        link = self.get_first_tag(channel, 'atom:link', False)

        return {
            'title': self.first_tag_text(channel, 'title'),
            'subtitle': self.first_tag_text(channel, 'itunes:subtitle', ''),
            'author': self.first_tag_text(
                channel, 'itunes:author', '(Unknown)'
            ),
            'copyright': self.first_tag_text(channel, 'copyright', ''),
            'owner_name': self.first_tag_text(channel, 'itunes:name', ''),
            'owner_email': self.first_tag_text(channel, 'itunes:email', ''),
            'summary': self.first_tag_text(channel, 'itunes:summary', ''),
            'description': self.first_tag_text(channel, 'description', ''),
            'language': self.first_tag_text(channel, 'language', ''),
            'explicit': self.first_tag_text(channel, 'itunes:explicit', ''),
            'link': link and link.get('href') or '',
            'image': image and image.get('href') or ''
        }

    def get_categories(self, root):
        rss = self.get_first_tag(root, 'rss')
        channel = self.get_first_tag(root, 'channel')
        categories = []

        for cat_el in channel.findAll('itunes:category'):
            cat = cat_el.get('text')
            if not cat:
                continue

            if cat_el.parent.name.lower() == 'itunes:category':
                parent = cat_el.parent.get('text')
                if parent in categories:
                    categories.pop(
                        categories.index(parent)
                    )

                    categories.append((parent, cat))
            else:
                categories.append(cat)

        return categories

    def get_items(self, root):
        rss = self.get_first_tag(root, 'rss')
        for item in rss.findAll('item'):
            if self.get_first_tag(item, 'enclosure', ''):
                yield item

    def get_item_data(self, root, item):
        enclosure_url = self.first_tag_attr(item, 'enclosure', 'url')
        enclosure_type = self.first_tag_attr(
            item,
            'enclosure',
            'type'
        )

        enclosure_size = self.first_tag_attr(
            item,
            'enclosure',
            'length'
        )

        enclosure_duration = self.first_tag_text(
            item,
            'itunes:duration'
        )

        if not enclosure_type:
            from mimetypes import guess_type
            from urllib.parse import urlparse

            urlparts = urlparse(enclosure_url)
            mimetype, encoding = guess_type(urlparts.path)
            enclosure_type = mimetype

        image = self.get_first_tag(item, 'itunes:image', False)

        return {
            'id': self.first_tag_text(item, 'guid', ''),
            'url': self.first_tag_text(item, 'link', ''),
            'title': self.first_tag_text(item, 'title'),
            'subtitle': self.first_tag_text(item, 'itunes:subtitle', ''),
            'season_number': self.first_tag_text(item, 'itunes:season', ''),
            'episode_number': self.first_tag_text(item, 'itunes:episode', ''),
            'date': self.first_tag_text(item, 'pubdate', ''),
            'description': self.first_tag_html(
                item,
                'content:encoded',
                self.first_tag_text(
                    item,
                    'description',
                    self.first_tag_text(
                        item,
                        'summary',
                        ''
                    )
                )
            ),
            'duration': self.first_tag_text(item, 'itunes:duration', ''),
            'summary': self.first_tag_text(item, 'itunes:summary', ''),
            'keywords': self.first_tag_text(item, 'itunes:keywords', ''),
            'enclosure_url': enclosure_url,
            'enclosure_type': enclosure_type,
            'enclosure_size': enclosure_size,
            'enclosure_duration': enclosure_duration,
            'image': image and image['href'] or None
        }


class RssAsHtmlImporter(RssImporter):
    verbose_name = 'Malformed RSS'

    def apply(self, data):
        root = BeautifulSoup(data, 'html.parser')

        if root is not None:
            channel = self.get_first_tag(root, 'channel', False)
            if channel is not False:
                return root
