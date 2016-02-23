import unittest

from protector.parser.query_parser import QueryParser
from protector.rules import negative_groupby_statement


class TestNegativeGroupByStatements(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()
        self.negative_groupby_statement = negative_groupby_statement.RuleChecker()

    def test_negative_groupby(self):
        q = self.parser.parse("select * from test group by time(-100ms)")
        self.assertFalse(self.negative_groupby_statement.check(q).is_ok())
        q = self.parser.parse("select * from test group by time(-1s)")
        self.assertFalse(self.negative_groupby_statement.check(q).is_ok())
        q = self.parser.parse("select * from test group by time(-10h)")
        self.assertFalse(self.negative_groupby_statement.check(q).is_ok())
        q = self.parser.parse("select * from test group by time(-20w)")
        self.assertFalse(self.negative_groupby_statement.check(q).is_ok())

        q = self.parser.parse("select * from test group by time(100ms)")
        self.assertTrue(self.negative_groupby_statement.check(q).is_ok())
        q = self.parser.parse("select * from test group by time(1s)")
        self.assertTrue(self.negative_groupby_statement.check(q).is_ok())
        q = self.parser.parse("select * from test group by time(10h)")
        self.assertTrue(self.negative_groupby_statement.check(q).is_ok())
        q = self.parser.parse("select * from test group by time(20w)")
        self.assertTrue(self.negative_groupby_statement.check(q).is_ok())
