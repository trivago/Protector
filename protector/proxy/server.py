import sys
import ssl
import socket
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    """
    Server that handles requests in multiple threads
    """
    daemon_threads = True

    def server_bind(self):
        HTTPServer.server_bind(self)

    def handle_error(self, request, client_address):
        """
        Overwrite error handling to suppress socket/ssl related errors
        :param client_address: Address of client
        :param request: Request causing an error
        """
        cls, e = sys.exc_info()[:2]
        if cls is socket.error or cls is ssl.SSLError:
            pass
        else:
            return HTTPServer.handle_error(self, request, client_address)
