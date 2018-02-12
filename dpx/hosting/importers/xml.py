from bs4 import BeautifulSoup


class XmlMixin(object):
    def apply(self, data):
        return BeautifulSoup(data, 'lxml')

    def get_first_tag(self, dom, tag, default=None):
        item = dom.find(tag)
        if item is not None:
            return item

        if default is None:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        return default

    def first_tag_text(self, dom, tag, default=None):
        item = dom.find(tag)

        if item is not None:
            return item.text

        if default is None:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        return default

    def first_tag_html(self, dom, tag, default=None):
        item = dom.find(tag)

        if item is not None:
            return '\n\n'.join(
                [
                    unicode(s) for s in item.contents
                    if unicode(s) != ']]>'
                ]
            )

        if default is None:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        return default

    def first_tag_attr(self, dom, tag, attribute, default=''):
        item = dom.find(tag)
        value = None

        if item is not None:
            try:
                value = item[attribute]
            except KeyError:
                pass
        else:
            raise Exception(
                'Could not find expected tag <%s> from %s' % (tag, dom.name)
            )

        if value is not None:
            return value

        if default is not None:
            return default

        raise Exception(
            'Node <%s> does not have expected attribute %s' % (
                item.name, attribute
            )
        )
