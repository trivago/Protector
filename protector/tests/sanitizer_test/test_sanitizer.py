import unittest
from protector.sanitizer import sanitizer


class TestSanitizer(unittest.TestCase):
    def setUp(self):
        self.sanitizer = sanitizer.Sanitizer()

    def test_parse_url(self):
        """
        Test url parsing
        """
        self.assertEqual(self.sanitizer.sanitize(""), "")
        self.assertEqual(self.sanitizer.sanitize("SELECT * fROm bla where X=Y"), "select * from bla where x=y")
        self.assertEqual(
                self.sanitizer.sanitize("select%20*%20from%20bla%20where%20x%3Dy"),
                "select * from bla where x=y"
        )
