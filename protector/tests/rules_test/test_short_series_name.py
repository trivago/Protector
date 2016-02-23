import unittest

from protector.query.delete import DeleteQuery
from protector.query.drop import DropQuery
from protector.query.list import ListQuery
from protector.query.select import SelectQuery
from protector.rules import short_series_name


class TestShortSeriesName(unittest.TestCase):
    def setUp(self):
        self.short_series_name = short_series_name.RuleChecker()

    def test_short_series_name(self):
        """
        Test prevention of queries with very short series names
        """
        self.assertFalse(self.short_series_name.check(SelectQuery('*', 'blub')).is_ok())
        self.assertFalse(self.short_series_name.check(SelectQuery('*', '/dus/')).is_ok())
        self.assertTrue(self.short_series_name.check(SelectQuery('my,fields', '/myseries.fjfjf/')).is_ok())
        self.assertFalse(self.short_series_name.check(DeleteQuery('myseries')).is_ok())
        self.assertFalse(self.short_series_name.check(DeleteQuery('/myseries/')).is_ok())
        self.assertFalse(self.short_series_name.check(DeleteQuery('/myseries/', 'time > now() - 24h')).is_ok())
        self.assertFalse(self.short_series_name.check(DropQuery('/myseries/')).is_ok())
        self.assertFalse(self.short_series_name.check(DropQuery('/my/')).is_ok())
        self.assertFalse(self.short_series_name.check(ListQuery('')).is_ok())
        self.assertFalse(self.short_series_name.check(ListQuery('//')).is_ok())
        self.assertFalse(self.short_series_name.check(ListQuery('bla')).is_ok())
        self.assertFalse(self.short_series_name.check(ListQuery('/myseries/')).is_ok())
        self.assertTrue(self.short_series_name.check(ListQuery('/myseries.is.long/')).is_ok())
