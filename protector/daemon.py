# -*- coding: utf-8 -*-

import logging
import sys

from protector.proxy import server
from protector.proxy import request_handler


class ProtectorDaemon(object):
    def __init__(self,
                 config,
                 protector,
                 handler_class=request_handler.ProxyRequestHandler,
                 server_class=server.ThreadingHTTPServer,
                 protocol="HTTP/1.1"
                 ):
        self.config = config
        self.protector = protector
        self.handler_class = handler_class
        self.server_class = server_class
        self.protocol = protocol

    def show_startup_message(self):
        logging.info("Serving Protector on {}:{}...".format(self.config.host, self.config.port))
        logging.info("Backend host (connection to Time Series Database) at {}:{}...".format(self.config.backend_host,
                                                                                            self.config.backend_port))
        logging.info("The following rules are enabled:")
        for rule in self.config.rules:
            logging.info("* {}".format(rule))
        if self.config.foreground:
            logging.info("Starting in foreground...")

    def configure_logging(self):
        logging.getLogger('').handlers = []
        logging_config = {
            "level": logging.DEBUG,
            "format": '%(asctime)s [%(levelname)s] %(message)s'
        }
        if self.config.foreground:
            logging_config["stream"] = sys.stdout
        else:
            logging_config["filename"] = self.config.logfile
            logging_config["filemode"] = "w"
        logging.basicConfig(**logging_config)

    def run(self):
        self.configure_logging()
        self.show_startup_message()
        logging.info('Daemon is starting')
        server_address = (self.config.host, self.config.port)
        backend_address = (self.config.backend_host, self.config.backend_port)

        # Subclassing BaseHTTPServer requires to pass args and kwargs to the parent class
        # but still there probably is a smarter way to do this...
        self.handler_class.protocol_version = self.protocol
        self.handler_class.protector = self.protector
        self.handler_class.backend_address = backend_address

        httpd = self.server_class(server_address, self.handler_class)
        self.serve_forever(httpd)

    @staticmethod
    def serve_forever(httpd):
        logging.info("Ready to handle requests.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            logging.info('^C received, shutting down.')
            httpd.socket.close()
