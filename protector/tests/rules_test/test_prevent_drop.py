import unittest

from protector.query.delete import DeleteQuery
from protector.query.drop import DropQuery
from protector.query.list import ListQuery
from protector.query.select import SelectQuery
from protector.rules import prevent_drop


class TestPreventDrop(unittest.TestCase):
    def setUp(self):
        self.prevent_drop = prevent_drop.RuleChecker()

    def test_prevent_drop(self):
        """
        Test prevention of DROP queries
        """
        self.assertFalse(self.prevent_drop.check(DropQuery('/myseries/')).is_ok())
        self.assertTrue(self.prevent_drop.check(DeleteQuery('myseries')).is_ok())
        self.assertTrue(self.prevent_drop.check(DeleteQuery('/myseries/')).is_ok())
        self.assertTrue(self.prevent_drop.check(DeleteQuery('/myseries/', 'time > now() - 24h')).is_ok())
        self.assertTrue(self.prevent_drop.check(SelectQuery('*', 'myseries')).is_ok())
        self.assertTrue(self.prevent_drop.check(ListQuery('/myseries/')).is_ok())
