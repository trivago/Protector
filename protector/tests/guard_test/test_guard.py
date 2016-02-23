import unittest
from protector.guard.guard import Guard
from protector.parser.query_parser import QueryParser
from protector.rules.rule_list import all_rules


class TestGuard(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()

    def test_guard(self):
        # Test rules loading
        guard = Guard(all_rules)
        q = self.parser.parse("select * from 'my.awesome.series' where time > now()-24h")
        self.assertTrue(guard.is_allowed(q))
