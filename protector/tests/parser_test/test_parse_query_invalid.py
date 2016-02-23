import unittest

from protector.parser.query_parser import QueryParser
from protector.tests.fixtures.loader import load_fixture


class TestParseInvalid(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_invalid_queries(self):
        """
        Test invalid queries
        """
        self.assertIsNone(self.parser.parse(None))
        self.assertIsNone(self.parser.parse("hello"))
        self.assertIsNone(self.parser.parse("select"))
        self.assertIsNone(self.parser.parse("select *"))
        self.assertIsNone(self.parser.parse("select * from"))

    def test_naughty_strings(self):
        """
        Test malicious user input
        """
        strings = load_fixture('naughty-strings/blns.txt')
        for string in strings:
            self.assertIsNone(self.parser.parse(string))
