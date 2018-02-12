from . import ImporterBase
from .xml import XmlMixin
from bs4 import BeautifulSoup
from mimetypes import guess_type
from urlparse import urlparse
import requests


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
        def get_enclosure_type(url):
            enclosure_type = self.first_tag_attr(
                item,
                'enclosure',
                'type'
            )

            if enclosure_type:
                return enclosure_type

            urlparts = urlparse(url)
            mimetype, encoding = guess_type(urlparts.path)

            if mimetype is None:
                response = requests.get(
                    url,
                    headers={
                        'User-Agent': (
                            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) '
                            'AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 '
                            'Mobile/14A300 Safari/602.1'
                        ),
                        'Accept-Encoding': None
                    },
                    stream=True
                )

                response.raise_for_status()
                return response.headers['content-type']

            return mimetype

        def get_enclosure_size():
            enclosure_size = self.first_tag_attr(
                item,
                'enclosure',
                'length'
            )

            try:
                enclosure_size = int(enclosure_size)
            except:
                enclosure_size = None

            if enclosure_size and enclosure_size >= 480000:
                return enclosure_size

            try:
                response = requests.head(
                    enclosure_url,
                    headers={
                        'User-Agent': (
                            'Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) '
                            'AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 '
                            'Mobile/14A300 Safari/602.1'
                        ),
                        'Accept-Encoding': None
                    },
                    allow_redirects=True
                )

                response.raise_for_status()
                return response.headers['content-length']
            except:
                return 28800000

        def get_enclosure_duration(filesize):
            try:
                enclosure_duration = self.first_tag_text(
                    item,
                    'itunes:duration'
                )
            except:
                enclosure_duration = None

            if enclosure_duration and 'NaN' in enclosure_duration:
                enclosure_duration = None

            if not enclosure_duration:
                enclosure_duration = unicode(int(float(filesize) / 12800.0))
            else:
                enclosure_duration = unicode(enclosure_duration)

            if ':' in enclosure_duration:
                while enclosure_duration.endswith(':'):
                    enclosure_duration = enclosure_duration[:-1]

                return enclosure_duration

            try:
                return unicode(int(enclosure_duration))
            except:
                return unicode(int(float(filesize) / 12800.0))

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
            'summary': self.first_tag_text(item, 'itunes:summary', ''),
            'keywords': self.first_tag_text(item, 'itunes:keywords', ''),
            'season': self.first_tag_text(item, 'itunes:season', '1'),
            'episode': self.first_tag_text(item, 'itunes:episode', ''),
            'episode_type': self.first_tag_text(item, 'itunes:episodeType', 'episode'),
            'enclosure_url': enclosure_url,
            'enclosure_type': get_enclosure_type,
            'enclosure_size': get_enclosure_size,
            'enclosure_duration': get_enclosure_duration,
            'image': image and image.get('href') or None
        }


class RssAsHtmlImporter(RssImporter):
    verbose_name = 'Malformed RSS'

    def apply(self, data):
        root = BeautifulSoup(data, 'html.parser')

        if root is not None:
            channel = self.get_first_tag(root, 'channel', False)
            if channel is not False:
                return root
