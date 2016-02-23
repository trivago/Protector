import unittest
from datetime import timedelta, datetime
from freezegun import freeze_time

from protector.influxdb.daterange import DateRange
from protector.influxdb.time_expression import TimeExpression
from protector.parser.subparsers.duration import DurationParser


@freeze_time("2015-11-04")
class TestParseDuration(unittest.TestCase):
    def test_durations(self):
        """
        Test simple time durations (i.e. only one time condition in the where clause)
        """
        now = datetime.now()
        epoch = TimeExpression.INFLUXDB_EPOCH
        d = DurationParser()
        self.assertEqual(d.parse([DateRange(now - timedelta(hours=2), now)]).timespan_seconds(), 2 * 60 * 60)
        self.assertEqual(d.parse([DateRange(now - timedelta(seconds=12), now)]).timespan_seconds(), 12)
        self.assertEqual(d.parse([DateRange(now - timedelta(weeks=23), now)]).timespan_seconds(), 23 * 7 * 24 * 60 * 60)
        # Times in the future will result in a duration of 0 seconds
        self.assertEqual(d.parse([DateRange(now + timedelta(microseconds=100), now)]).timespan_seconds(), 0)
        self.assertEqual(d.parse([DateRange(now - timedelta(microseconds=100), now - timedelta(microseconds=100))]).timespan_seconds(), 0)
        self.assertEqual(d.parse([DateRange(epoch, datetime(2014, 8, 23))]).timespan_seconds(), 24 * 60 * 60)
        self.assertEqual(d.parse([DateRange(datetime(2013, 11, 4, 9, 30, 0, 232000), now)]).timespan_seconds(), 63037799.768)
        self.assertEqual(d.parse([DateRange(datetime(2013, 8, 10), datetime(2013, 8, 20)),
                                  DateRange(datetime(2013, 8, 12), datetime(2013, 8, 18))]).timespan_seconds(), 6 * 24 * 60 * 60)
        self.assertEqual(d.parse([DateRange(datetime(2013, 8, 12), datetime(2013, 8, 20)),
                                  DateRange(datetime(2013, 8, 10), datetime(2013, 8, 18))]).timespan_seconds(), 6 * 24 * 60 * 60)
        self.assertEqual(d.parse([DateRange(datetime(2013, 8, 12), datetime(2013, 8, 20)),
                                  DateRange(datetime(2014, 8, 12), datetime(2014, 8, 20))]).timespan_seconds(), 0)
        self.assertEqual(d.parse([DateRange(datetime(2013, 8, 2, 23, 1, 10), now)]).timespan_seconds(), 71110730)
