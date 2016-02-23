import unittest

from protector.parser.query_parser import QueryParser
from protector.rules import query_old_data


class TestQueryForOldData(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()
        self.query_old_data = query_old_data.RuleChecker()

    def test_single_timedelta(self):
        """
        Select queries may not query data that is too old
        """
        for big_timedelta in ["20d", "22w", "50000m", "10010h", "1000000s"]:
            self.assertFalse(self.query_old_data.check(
                self.parser.parse(
                    "select * from 'myseries' where time > now() - {}".format(big_timedelta))
            ).is_ok())

        for small_timedelta in ["10s", "1h", "50m"]:
            self.assertTrue(self.query_old_data.check(
                self.parser.parse(
                    "select * from 'myseries' where time > now() - {}".format(small_timedelta))
            ).is_ok())

    def test_multiple_timedeltas(self):
        self.assertTrue(self.query_old_data.check(
            self.parser.parse(
                "select mean(value) from 'myseries' where time > now() - 2d and time < now() - 1d"
            )).is_ok())
