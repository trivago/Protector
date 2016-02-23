import unittest
from freezegun import freeze_time
from datetime import datetime, timedelta

from protector.influxdb.keyword import Keyword
from protector.influxdb.resolution import Resolution
from protector.influxdb.time_expression import TimeExpression
from protector.parser.query_parser import QueryParser


# For the following unit tests we assume the current data is five days after INFLUXDB_EPOCH
@freeze_time((TimeExpression.INFLUXDB_EPOCH + timedelta(days=5)).strftime("%Y-%m-%d"))
class TestParseSelect(unittest.TestCase):
    def setUp(self):
        self.parser = QueryParser()
        self.default_resolution = Resolution.MAX_RESOLUTION

    def test_simple_select_query(self):
        """
        Test simple SELECT Queries
        """
        query = self.parser.parse("select * from mymetric")
        self.assertEqual(query.get_type(), Keyword.SELECT)
        self.assertEqual(query.select_stmt, "*")
        self.assertEqual(query.from_stmt, "mymetric")
        self.assertIsNone(query.where_stmt)
        self.assertIsNone(query.limit_stmt)
        self.assertIsNone(query.group_by_stmt)
        self.assertEqual(query.resolution, self.default_resolution)
        self.assertEqual(query.datapoints, 5 * 24 * 60 * 6)
        self.assertEqual(query.get_earliest_date(), TimeExpression.INFLUXDB_EPOCH)

    def test_complex_select_query(self):
        """
        Test complex SELECT queries
        """
        query = self.parser.parse("select value, test from /my.regex/ where time > now() - 24h limit 10")
        self.assertEqual(query.get_type(), Keyword.SELECT)
        self.assertEqual(query.select_stmt, "value, test")
        self.assertEqual(query.from_stmt, "/my.regex/")
        self.assertEqual(query.where_stmt, "time > now() - 24h")
        self.assertEqual(query.limit_stmt, '10')
        self.assertIsNone(query.group_by_stmt)
        self.assertEqual(query.resolution, self.default_resolution)
        self.assertEqual(query.datapoints, 10)
        self.assertEqual(query.get_earliest_date(), datetime.now() - timedelta(days=1))

    def test_group_by(self):
        """
        Test SELECT queries with group by statement
        """
        query = self.parser.parse('select * from "series" where time > now() - 24h group by time(10m)')
        self.assertEqual(query.get_type(), Keyword.SELECT)
        self.assertEqual(query.select_stmt, "*")
        self.assertEqual(query.from_stmt, '"series"')
        self.assertEqual(query.where_stmt, "time > now() - 24h")
        self.assertIsNone(query.limit_stmt)
        self.assertEqual(query.group_by_stmt, "time(10m)")
        self.assertEqual(query.resolution, 10 * 60)
        self.assertEqual(query.datapoints, (24 * 60 * 60) / (10 * 60))
        self.assertEqual(query.get_earliest_date(), datetime.now() - timedelta(days=1))

        query = self.parser.parse('select count(type) from events group by time(10m), type;')
        self.assertEqual(query.get_type(), Keyword.SELECT)
        self.assertEqual(query.select_stmt, "count(type)")
        self.assertEqual(query.from_stmt, 'events')
        self.assertIsNone(query.where_stmt)
        self.assertIsNone(query.limit_stmt)
        self.assertEqual(query.group_by_stmt, "time(10m), type")
        self.assertEqual(query.resolution, 10 * 60)
        self.assertEqual(query.datapoints, (5 * 24 * 60 * 60) / (10 * 60))
        self.assertEqual(query.get_earliest_date(), TimeExpression.INFLUXDB_EPOCH)

        query = self.parser.parse('select percentile(value, 95) from response_times group by time(30s);')
        self.assertEqual(query.get_type(), Keyword.SELECT)
        self.assertEqual(query.select_stmt, "percentile(value, 95)")
        self.assertEqual(query.from_stmt, 'response_times')
        self.assertIsNone(query.where_stmt)
        self.assertIsNone(query.limit_stmt)
        self.assertEqual(query.group_by_stmt, "time(30s)")
        self.assertEqual(query.resolution, 30)
        self.assertEqual(query.datapoints, (5 * 24 * 60 * 60) / 30)
        self.assertEqual(query.get_earliest_date(), TimeExpression.INFLUXDB_EPOCH)

    def test_merge(self):
        query = self.parser.parse('select count(type) from user_events merge admin_events group by time(10m)')
        self.assertEqual(query.get_type(), Keyword.SELECT)
        self.assertEqual(query.select_stmt, "count(type)")
        self.assertEqual(query.from_stmt, 'user_events merge admin_events')
        self.assertIsNone(query.where_stmt)
        self.assertIsNone(query.limit_stmt)
        self.assertEqual(query.group_by_stmt, "time(10m)")
        self.assertEqual(query.resolution, 10 * 60)
        self.assertEqual(query.datapoints, (5 * 24 * 60 * 60) / (10 * 60))
        self.assertEqual(query.get_earliest_date(), TimeExpression.INFLUXDB_EPOCH)

    def test_multiple_times(self):
        query = self.parser.parse("select * from 's' where time > now() - 2d and time < now() - 1d")
        self.assertEqual(query.get_type(), Keyword.SELECT)
        self.assertEqual(query.select_stmt, "*")
        self.assertEqual(query.from_stmt, "'s'")
        self.assertEqual(query.where_stmt, "time > now() - 2d and time < now() - 1d")
        self.assertIsNone(query.limit_stmt)
        self.assertIsNone(query.group_by_stmt)
        self.assertEqual(query.resolution, self.default_resolution)
        self.assertEqual(query.datapoints, (24 * 60 * 60) / 10)
        self.assertEqual(query.get_earliest_date(), datetime.now() - timedelta(days=2))
