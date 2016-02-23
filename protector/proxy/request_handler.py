import os
import socket
import ssl
import select
import httplib
import urlparse
import threading
import gzip
import zlib
import time
import logging
import urllib
from BaseHTTPServer import BaseHTTPRequestHandler
from cStringIO import StringIO
from subprocess import Popen, PIPE

from protector.proxy.http_request import HTTPRequest


class ProxyRequestHandler(BaseHTTPRequestHandler):
    protector = None
    backend_address = None

    cakey = 'ca.key'
    cacert = 'ca.crt'
    certkey = 'cert.key'
    certdir = 'certs/'

    # Request timeout
    timeout = 60
    lock = threading.Lock()

    def __init__(self, *args, **kwargs):
        self.tls = threading.local()
        self.version_table = {10: 'HTTP/1.0', 11: 'HTTP/1.1'}
        self.http_request = HTTPRequest()

        # Address to time series backend
        backend_host, backend_port = self.backend_address
        self.backend_netloc = "{}:{}".format(backend_host, backend_port)

        self.path = None
        self.connection = None
        self.rfile = None
        self.wfile = None
        self.close_connection = 0

        BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

    def log_error(self, log_format, *args):
        # Suppress "Request timed out: timeout('timed out',)"
        if isinstance(args[0], socket.timeout):
            return
        self.log_message(log_format, *args)

    def do_CONNECT(self):
        if os.path.isfile(self.cakey) and os.path.isfile(self.cacert) and os.path.isfile(self.certkey):
            if os.path.isdir(self.certdir):
                self.connect_intercept()
        self.connect_relay()

    def connect_intercept(self):
        hostname = self.path.split(':')[0]
        certpath = "%s/%s.crt" % (self.certdir.rstrip('/'), hostname)

        with self.lock:
            if not os.path.isfile(certpath):
                epoch = "%d" % (time.time() * 1000)
                p1 = Popen(["openssl", "req", "-new", "-key", self.certkey, "-subj", "/CN=%s" % hostname], stdout=PIPE)
                p2 = Popen(["openssl", "x509", "-req", "-days", "3650", "-CA", self.cacert, "-CAkey", self.cakey,
                            "-set_serial", epoch, "-out", certpath], stdin=p1.stdout, stderr=PIPE)
                p2.communicate()

        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, httplib.OK, 'Connection Established'))
        self.end_headers()

        self.connection = ssl.wrap_socket(self.connection, keyfile=self.certkey, certfile=certpath, server_side=True)
        self.rfile = self.connection.makefile("rb", self.rbufsize)
        self.wfile = self.connection.makefile("wb", self.wbufsize)

        conntype = self.headers.get('Proxy-Connection', '')
        if conntype.lower() == 'close':
            self.close_connection = 1
        elif conntype.lower() == 'keep-alive' and self.protocol_version >= "HTTP/1.1":
            self.close_connection = 0

    def connect_relay(self):
        address = self.path.split(':', 1)
        address[1] = int(address[1]) or 443
        try:
            s = socket.create_connection(address, timeout=self.timeout)
        except:
            self.send_error(httplib.BAD_GATEWAY)
            return
        self.send_response(httplib.OK, 'Connection Established')
        self.end_headers()

        conns = [self.connection, s]
        self.close_connection = 0
        while not self.close_connection:
            rlist, wlist, xlist = select.select(conns, [], conns, self.timeout)
            if xlist or not rlist:
                break
            for r in rlist:
                other = conns[1] if r is conns[0] else conns[0]
                data = r.recv(8192)
                if not data:
                    self.close_connection = 1
                    break
                other.sendall(data)

    def _check_query(self, query_string):
        """
        Check if the query_string is allowed by the Protector rule set
        """
        return self.protector.check(query_string)

    @staticmethod
    def get_queries(parameters):
        """
        Get a list of all queries (q=... parameters) from an URL parameter string
        :param parameters: The url parameter list
        """
        parsed_params = urlparse.parse_qs(parameters)
        if 'q' not in parsed_params:
            return []
        queries = parsed_params['q']

        # Check if only one query string is given
        # in this case make it a list
        if not isinstance(queries, list):
            queries = [queries]
        return queries

    @staticmethod
    def _analyze_url(path):
        url_parts = urlparse.urlsplit(path)
        parameters = url_parts.query if url_parts.query else url_parts.path
        scheme, netloc, path = url_parts.scheme, url_parts.netloc, (url_parts.path + '?' + parameters)
        assert scheme in ('http', 'https')
        return scheme, netloc, path, parameters

    def do_GET(self):
        self.path = self._build_url(self.path, self.headers['Host'])
        scheme, netloc, path, parameters = self._analyze_url(self.path)

        queries = self.get_queries(parameters)

        for query_string in queries:
            query_result = self._check_query(query_string)
            if not query_result.is_ok():
                logging.warning("Query blocked: %s. Reason: %s", query_string, query_result.value)
                self.send_error(httplib.BAD_REQUEST, query_result.value)
                return
            logging.debug("Query ok: %s", query_string)

        # TODO: Is this needed?
        # self.headers['Host'] = self.backend_netloc
        self.filter_headers(self.headers)
        self._handle_request(scheme, self.backend_netloc, path, self.headers)

    def _handle_request(self, scheme, netloc, path, headers, body=None, method="GET"):
        """
        Run the actual request
        """
        backend_url = "{}://{}{}".format(scheme, netloc, path)
        try:
            response = self.http_request.request(backend_url, method=method, body=body, headers=dict(headers))
            self._return_response(response)
        except Exception as e:
            body = "Invalid response from backend: '{}' Server might be busy".format(e.message)
            logging.debug(body)
            self.send_error(httplib.SERVICE_UNAVAILABLE, body)

    def do_POST(self):
        self.path = self._build_url(self.path, self.headers['Host'])
        scheme, netloc, path, parameters = self._analyze_url(self.path)

        length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(length)

        self.filter_headers(self.headers)
        self._handle_request(scheme, self.backend_netloc, path, self.headers, body=post_data, method="POST")

    def send_error(self, code, message=None):
        """
        Send and log plain text error reply.
        :param code:
        :param message:
        """
        message = message.strip()
        self.log_error("code %d, message %s", code, message)
        self.send_response(code)
        self.send_header("Content-Type", "text/plain")
        self.send_header('Connection', 'close')
        self.end_headers()
        if message:
            self.wfile.write(message)

    def _return_response(self, response):
        """
        :type result: HTTPResponse
        """
        self.filter_headers(response.msg)
        if "content-length" in response.msg:
            del response.msg["content-length"]

        self.send_response(response.status, response.reason)
        for header_key, header_value in response.msg.items():
            self.send_header(header_key, header_value)
        body = response.read()
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    do_HEAD = do_GET
    do_OPTIONS = do_GET

    @staticmethod
    def filter_headers(headers):
        # http://tools.ietf.org/html/rfc2616#section-13.5.1
        hop_by_hop = (
            'connection', 'keep-alive', 'proxy-authenticate', 'proxy-authorization', 'te', 'trailers',
            'transfer-encoding', 'upgrade'
        )
        for k in hop_by_hop:
            if k in headers:
                del headers[k]

    @staticmethod
    def encode_content_body(text, encoding):
        if encoding == 'identity':
            return text
        if encoding in ('gzip', 'x-gzip'):
            io = StringIO()
            with gzip.GzipFile(fileobj=io, mode='wb') as f:
                f.write(text)
            return io.getvalue()
        if encoding == 'deflate':
            return zlib.compress(text)
        raise Exception("Unknown Content-Encoding: %s" % encoding)

    @staticmethod
    def decode_content_body(data, encoding):
        if encoding == 'identity':
            return data
        if encoding in ('gzip', 'x-gzip'):
            io = StringIO(data)
            with gzip.GzipFile(fileobj=io) as f:
                return f.read()
        if encoding == 'deflate':
            return zlib.decompress(data)

        raise Exception("Unknown Content-Encoding: %s" % encoding)

    def send_cacert(self):
        with open(self.cacert, 'rb') as f:
            data = f.read()

        self.wfile.write("%s %d %s\r\n" % (self.protocol_version, httplib.OK, 'OK'))
        self.send_header('Content-Type', 'application/x-x509-ca-cert')
        self.send_header('Content-Length', len(data))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(data)

    def _build_url(self, path, host):
        if path[0] != '/':
            return path
        if isinstance(self.connection, ssl.SSLSocket):
            return "https://%s%s" % (host, path)
        else:
            return "http://%s%s" % (host, path)
