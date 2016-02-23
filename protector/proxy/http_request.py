from httplib import HTTPSConnection, HTTPConnection, IncompleteRead
import urlparse
import threading


class HTTPRequest(object):
    """
    A simple, thread-safe wrapper around HTTP(S)Connection
    """

    def __init__(self):
        self.tls = threading.local()
        self.tls.conns = {}

    def request(self, url, body=None, headers=None, timeout=45, max_retries=3, method="GET"):
        if headers is None:
            headers = dict()

        parsed = urlparse.urlsplit(url)
        origin = (parsed.scheme, parsed.netloc)

        for i in range(1, max_retries):
            try:
                conn = self.create_conn(parsed, origin, timeout)
                conn.request(method, url, body=body, headers=headers)
                return conn.getresponse()
            except IncompleteRead as e:
                return e.partial
            except Exception as e:
                if origin in self.tls.conns:
                    del self.tls.conns[origin]
                if i >= max_retries:
                    raise e

    def create_conn(self, parsed, origin, timeout):
        if origin not in self.tls.conns:
            if parsed.scheme == 'https':
                self.tls.conns[origin] = HTTPSConnection(parsed.netloc, timeout=timeout)
            else:
                self.tls.conns[origin] = HTTPConnection(parsed.netloc, timeout=timeout)
        return self.tls.conns[origin]
