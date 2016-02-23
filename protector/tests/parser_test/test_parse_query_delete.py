import unittest

from protector.influxdb.keyword import Keyword
from protector.parser.query_parser import QueryParser


class TestParseDelete(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_delete_query(self):
        """
        Test parsing DELETE queries
        """
        query = self.parser.parse("delete from response_times where time < now() - 1h")
        self.assertEqual(query.get_type(), Keyword.DELETE)
        self.assertEqual(query.from_stmt, "response_times")
        self.assertEqual(query.where_stmt, "time < now() - 1h")

        query = self.parser.parse("delete from /^stats.*/ where time < now() - 7d")
        self.assertEqual(query.get_type(), Keyword.DELETE)
        self.assertEqual(query.from_stmt, "/^stats.*/")
        self.assertEqual(query.where_stmt, "time < now() - 7d")

        self.assertIsNone(self.parser.parse("delete from response_times where user = 'foo'"), None)
