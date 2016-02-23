import unittest

from protector.query.delete import DeleteQuery
from protector.query.drop import DropQuery
from protector.query.list import ListQuery
from protector.query.select import SelectQuery
from protector.rules import prevent_delete


class TestPreventDelete(unittest.TestCase):
    def setUp(self):
        self.prevent_delete = prevent_delete.RuleChecker()

    def test_prevent_delete(self):
        """
        Test prevention of DELETE queries
        """
        self.assertFalse(self.prevent_delete.check(DeleteQuery('myseries')).is_ok())
        self.assertFalse(self.prevent_delete.check(DeleteQuery('/myseries/')).is_ok())
        self.assertFalse(self.prevent_delete.check(DeleteQuery('/myseries/', 'time > now() - 24h')).is_ok())
        self.assertTrue(self.prevent_delete.check(SelectQuery('*', 'myseries')).is_ok())
        self.assertTrue(self.prevent_delete.check(ListQuery('/myseries/')).is_ok())
        self.assertTrue(self.prevent_delete.check(DropQuery('/myseries/')).is_ok())
