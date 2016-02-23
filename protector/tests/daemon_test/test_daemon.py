import unittest
import time
from mock import MagicMock, patch
import daemonocle
import threading
import sys

try:
    import __builtin__ as builtins  # pylint:disable=import-error
except ImportError:
    import builtins  # pylint:disable=import-error

from protector.daemon import ProtectorDaemon
from protector.config.loader import ObjectView


class TestDaemon(threading.Thread):
    def __init__(self, logfile, name="TestDaemon", foreground=True):
        threading.Thread.__init__(self, name=name)
        self.foreground = foreground
        self.logfile = logfile
        self.daemon = daemonocle.Daemon(detach=False, pidfile="./fakepidfile")
        self.keep_running = True
        self.protector = MagicMock()
        self.config = ObjectView({"foreground": self.foreground,
                                  "logfile": self.logfile,
                                  "host": "localhost",
                                  "port": 12340,
                                  "backend_host": "backend_host",
                                  "backend_port": "backend_port",
                                  "rules": []})

    def run(self):
        protector_daemon = ProtectorDaemon(config=self.config, protector=self.protector)
        self.daemon.worker = protector_daemon.run
        print("Starting daemon in {}".format("foreground" if self.foreground else "background"))

        with patch('os.open') as open, \
                patch('signal.signal') as signal:
            open.return_value = True
            self.daemon.do_action("start")

    def stop_daemon(self):
        self.daemon.do_action("stop")


class TestProtectorDaemon(unittest.TestCase):

    def start_stop_protector(self, foreground=True, mock_logfile="./fakelogfile"):
        daemon = TestDaemon(logfile=mock_logfile, foreground=foreground)
        daemon.start()
        time.sleep(1)
        daemon.stop_daemon()
        daemon.join()

    @unittest.skip("fixme")
    @patch("protector.daemon.logging")
    def test_foreground(self, mock_logging):
        """
        A logfile shall be written when the daemon is running in the background.
        If it's running in the foreground, it shall print to stdout
        """
        self.start_stop_protector(foreground=True)
        self.assertTrue(mock_logging.basicConfig.called)
        self.assertEqual(mock_logging.basicConfig.call_count, 1)
        positional_args, kwargs = mock_logging.basicConfig.call_args
        self.assertEqual(kwargs["stream"], sys.stdout)
        self.assertTrue("filename" not in kwargs)
        self.assertTrue(mock_logging.info.called)

    @unittest.skip("fixme")
    @patch("protector.daemon.logging")
    def test_background(self, mock_logging):
        """
        A logfile shall be written when the daemon is running in the background.
        If it's running in the foreground, it shall print to stdout
        """
        self.start_stop_protector(foreground=False, mock_logfile="./fakelogfile")
        self.assertTrue(mock_logging.basicConfig.called)
        self.assertEqual(mock_logging.basicConfig.call_count, 1)
        positional_args, kwargs = mock_logging.basicConfig.call_args
        self.assertEqual(kwargs["filename"], "./fakelogfile")
        self.assertTrue("stream" not in kwargs)
        self.assertTrue(mock_logging.info.called)
