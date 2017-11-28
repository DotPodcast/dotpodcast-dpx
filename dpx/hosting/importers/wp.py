from mimetypes import guess_type
from . import ImporterBase
from .xml import XmlMixin


class WordPressImporter(XmlMixin, ImporterBase):
    verbose_name = 'WordPress'

    def apply(self, data):
        root = super(WordPressImporter, self).apply(data)
        if root is not None:
            wp = self.first_tag_text(root, 'wp:wxr_version', False)

            if wp is False:
                return

            return root

    def get_podcast_data(self, root):
        channel = self.get_first_tag(root, 'channel')
        author = self.get_first_tag(channel, 'wp:author')
        first_name = self.first_tag_text(author, 'wp:author_first_name')
        last_name = self.first_tag_text(author, 'wp:author_last_name')

        return {
            'title': self.first_tag_text(channel, 'title'),
            'author': ('%s %s' % (first_name, last_name)).strip()
        }

    def get_categories(self, root):
        channel = self.get_first_tag(root, 'channel')

        for cat in channel.findAll('wp:category'):
            if self.first_tag_text(cat, 'wp:category_parent', ''):
                continue

            yield self.first_tag_text(cat, 'wp:cat_name')

    def get_items(self, root):
        rss = self.get_first_tag(root, 'rss')
        for item in rss.findAll('item'):
            if self.first_tag_text(item, 'wp:post_type', '') == 'post':
                yield item

    def get_item_data(self, root, item):
        rss = self.get_first_tag(root, 'rss')
        channel = self.get_first_tag(rss, 'channel')
        post_id = self.first_tag_text(item, 'wp:post_id')

        data = {
            'id': self.first_tag_text(item, 'link'),
            'title': self.first_tag_text(item, 'title'),
            'date': self.first_tag_text(item, 'pubdate'),
            'description': self.first_tag_html(item, 'content:encoded')
        }

        for alt in channel.findAll('item'):
            post_type = self.first_tag_text(alt, 'wp:post_type', '')
            if post_type == 'attachment':
                post_parent = self.first_tag_text(alt, 'wp:post_parent', '')
                if post_parent and post_id == post_parent:
                    attachment_url = self.first_tag_text(
                        alt, 'wp:attachment_url'
                    )

                    mimetype, encoding = guess_type(attachment_url)

                    if mimetype.startswith('audio/'):
                        data['enclosure_url'] = attachment_url
                        data['enclosure_type'] = mimetype
                    elif mimetype.startswith('image/'):
                        data['image'] = attachment_url

        return data
