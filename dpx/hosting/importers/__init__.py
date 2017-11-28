class ImporterBase(object):
    def apply(self, data):
        raise NotImplementedError('Method not implemented.')

    def get_podcast_data(self, root):
        raise NotImplementedError('Method not implemented.')

    def get_items(self, root):
        raise NotImplementedError('Method not implemented.')

    def get_item_data(self, root, item):
        raise NotImplementedError('Method not implemented.')
