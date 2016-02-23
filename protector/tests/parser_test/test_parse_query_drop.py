import unittest

from protector.influxdb.keyword import Keyword
from protector.parser.query_parser import QueryParser


class TestParseDrop(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_drop_query(self):
        """
        Test parsing DROP series queries
        """
        query = self.parser.parse("drop series response_times")
        self.assertEqual(query.get_type(), Keyword.DROP)
        self.assertEqual(query.series_stmt, "response_times")
