import unittest

from protector.influxdb.keyword import Keyword
from protector.parser.query_parser import QueryParser


class TestParseList(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_list_series_query(self):
        """
        Test LIST series queries
        """
        query = self.parser.parse('list series')
        self.assertEqual(query.get_type(), Keyword.LIST)
        self.assertEqual(query.series_stmt, '')
        print query

        query = self.parser.parse('list series /my_regex\.test/')
        self.assertEqual(query.get_type(), Keyword.LIST)
        self.assertEqual(query.series_stmt, '/my_regex\.test/')
        print query

        query = self.parser.parse('list series "my-awesome.series.name"')
        self.assertEqual(query.get_type(), Keyword.LIST)
        self.assertEqual(query.series_stmt, '"my-awesome.series.name"')
        print query
