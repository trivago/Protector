try:
    # Python 3.x
    from urllib.parse import urlparse, parse_qs
except ImportError:
    # Python 2.7
    from urlparse import urlparse, parse_qs


class UrlHandler(object):
    @staticmethod
    def get_query(url):
        parsed = urlparse(url)
        parameters = parse_qs(parsed.query)
        if 'q' in parameters:
            return ''.join(parameters['q'])
        return None
