class ImportingError(Exception):
    pass


class ImportingHTTPError(Exception):
    pass


class ValidationError(ImportingError):
    pass


class ViewError(Exception):
    pass


class InvalidContentTypeError(ViewError):
    pass


class InvalidTokenError(ViewError):
    pass
