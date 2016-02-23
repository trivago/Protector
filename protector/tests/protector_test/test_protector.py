import unittest
from urllib2 import quote

from protector.protector_main import Protector


class TestProtector(unittest.TestCase):
    def test_whitelist(self):
        protector = Protector(["too_many_datapoints"], ["^releases$", "^grafana\.", ".*java.*boot.*version.*"], True)
        self.assertTrue(protector.check(quote("select * from releases")).is_ok())
        self.assertFalse(protector.check(quote("select * from some.random.series.releases")).is_ok())
        self.assertFalse(protector.check(quote("select * from releases.are.important")).is_ok())

        self.assertTrue(protector.check(quote("select * from grafana.temp_dashboard_Y2hyb25vcy1qb2Jz")).is_ok())
        self.assertFalse(protector.check(quote("select * from bla.bla.grafana.")).is_ok())
        self.assertFalse(protector.check(quote("select * from grafana")).is_ok())

        query = "select tags,title,text_details from merge(/app4\.java\.boot\.version\./) where time > now() - 7d"
        self.assertTrue(protector.check(quote(query)).is_ok())

        protector = Protector(["too_many_datapoints"], [], True)
        self.assertFalse(protector.check(quote("select * from grafana")).is_ok())

    def test_unknown_queries_safe_mode(self):
        protector = Protector(["prevent_delete"], [], True)
        self.assertTrue(protector.check("").is_ok())
        self.assertTrue(protector.check("asdf").is_ok())

    def test_unknown_queries_non_safe_mode(self):
        protector = Protector(["prevent_delete"], [], False)
        self.assertFalse(protector.check("").is_ok())
        self.assertFalse(protector.check("asdf").is_ok())

    def test_valid_queries(self):
        # Set protector to unsafe mode
        protector = Protector(["prevent_delete"], [], False)
        self.assertTrue(protector.check(quote("select * from bla where x=y")).is_ok())
