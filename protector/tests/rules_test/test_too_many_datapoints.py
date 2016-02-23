import unittest

from protector.parser.query_parser import QueryParser
from protector.query.select import SelectQuery
from protector.rules import too_many_datapoints


class TestTooManyDatapoints(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()
        self.too_many_datapoints = too_many_datapoints.RuleChecker()

    def test_small_number_of_datapoints(self):
        """
        Select queries with a reasonable number of datapoints shall be allowed
        """
        self.assertTrue(self.too_many_datapoints.check(
                SelectQuery('*', '/myseries/', where_stmt='time > now() - 24h')
        ).is_ok())

        self.assertTrue(self.too_many_datapoints.check(
                self.parser.parse(
                        "select * from 'server.search.item.standard-average' where time > now()-24h")
        ).is_ok())

        self.assertTrue(self.too_many_datapoints.check(
                self.parser.parse(
                        'select * from /host.df_complex-free/ where time > now()-30d group by time(12h) order asc')
        ).is_ok())

        self.assertTrue(self.too_many_datapoints.check(
                self.parser.parse("select * from /test/ where time > now()-7d group by time(1h)")
        ).is_ok())

        self.assertTrue(self.too_many_datapoints.check(
                self.parser.parse(
                        "select * from /^myseries/ where value > -1 and time > now() - 1w GROUP by time(30s) limit 10")
        ).is_ok())

        self.assertTrue(self.too_many_datapoints.check(
                SelectQuery('*', '/myseries/', where_stmt='time > now() - 25h')
        ).is_ok())

        self.assertTrue(self.too_many_datapoints.check(
                self.parser.parse("select * from /test/ where time > now()-7d group by time(10m)")
        ).is_ok())

    def test_big_number_of_datapoints(self):
        self.assertFalse(self.too_many_datapoints.check(
                self.parser.parse("select * from /test/ where time > now()-7d group by time(1m)")
        ).is_ok())

        self.assertFalse(self.too_many_datapoints.check(
                self.parser.parse("select median(value) from /test/ where time > now()-30d group by time(15s)")
        ).is_ok())

        self.assertFalse(self.too_many_datapoints.check(
                self.parser.parse(
                        "select * from /^mylongseriesname/ where value > -1 and time > now() - 1w GROUP by time(30s)")
        ).is_ok())

        self.assertFalse(self.too_many_datapoints.check(
                self.parser.parse("select * from /my.dashboard_.*/ where title =~ /.*.*/i")
        ).is_ok())
