import unittest

from protector.query.delete import DeleteQuery
from protector.query.drop import DropQuery
from protector.query.list import ListQuery
from protector.query.select import SelectQuery
from protector.rules import series_endswith_dot


class TestEndsWithDot(unittest.TestCase):
    def setUp(self):
        self.series_endswith_dot = series_endswith_dot.RuleChecker()

    def test_series_endswith_dot(self):
        """
        Test prevention of queries that end with a dot
        """
        self.assertFalse(self.series_endswith_dot.check(SelectQuery('*', 'blub.')).is_ok())
        self.assertTrue(self.series_endswith_dot.check(SelectQuery('*', 'blub\.')).is_ok())
        self.assertFalse(self.series_endswith_dot.check(SelectQuery('*', '/dus./')).is_ok())
        self.assertFalse(self.series_endswith_dot.check(DeleteQuery('myseries.')).is_ok())
        self.assertFalse(self.series_endswith_dot.check(DeleteQuery('/myseries./')).is_ok())
        self.assertTrue(self.series_endswith_dot.check(DeleteQuery('/myseries\./')).is_ok())
        self.assertTrue(self.series_endswith_dot.check(DeleteQuery('/myseries/', 'time > now() - 24h')).is_ok())
        self.assertTrue(self.series_endswith_dot.check(ListQuery('/myseries/')).is_ok())
        self.assertFalse(self.series_endswith_dot.check(ListQuery('/myseries./')).is_ok())
        self.assertFalse(self.series_endswith_dot.check(DropQuery('/myseries./')).is_ok())
        self.assertTrue(self.series_endswith_dot.check(DropQuery('/myseries/')).is_ok())
