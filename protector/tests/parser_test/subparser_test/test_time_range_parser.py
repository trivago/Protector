from freezegun import freeze_time
from datetime import datetime, timedelta
import unittest

from protector.influxdb.daterange import DateRange
from protector.influxdb.time_expression import TimeExpression
from protector.parser.subparsers.time_range import TimeRangeParser


@freeze_time("2015-12-24")  # Ho ho ho!
class TestParseTimeRange(unittest.TestCase):
    def test_invalid_duration(self):
        """
        Test invalid time durations
        """
        self.assertEqual(TimeRangeParser().parse(None), [])
        self.assertEqual(TimeRangeParser().parse("hello"), [])
        self.assertEqual(TimeRangeParser().parse("tim"), [])
        self.assertEqual(TimeRangeParser().parse("t ime"), [])
        self.assertEqual(TimeRangeParser().parse("time 122 now()"), [])
        self.assertEqual(TimeRangeParser().parse("time ~ now()"), [])
        self.assertEqual(TimeRangeParser().parse("999"), [])

    def test_relative_times(self):
        """
        Test relative time statements
        """
        t = TimeRangeParser()
        now = datetime.now()
        epoch = TimeExpression.INFLUXDB_EPOCH
        self.assertEqual(t.parse("time > now() - 2h"), [DateRange(now - timedelta(hours=2), now)])
        self.assertEqual(t.parse("time > now() - 12s"), [DateRange(now - timedelta(seconds=12), now)])
        self.assertEqual(t.parse("time > now() - 23w"), [DateRange(now - timedelta(weeks=23), now)])
        # If no unit is given the value is interpreted as microseconds.
        self.assertEqual(t.parse("time > now() + 100"),
                         [DateRange(now + timedelta(microseconds=100), now)])
        self.assertEqual(t.parse("time > now() + 100u"),
                         [DateRange(now + timedelta(microseconds=100), now)])
        self.assertEqual(t.parse("time < now() + 100u"),
                         [DateRange(epoch, now + timedelta(microseconds=100))])
        self.assertEqual(t.parse("time = now() + 100u"),
                         [DateRange(now + timedelta(microseconds=100), now + timedelta(microseconds=100))])
        self.assertEqual(t.parse("time = now() - 100u"),
                         [DateRange(now - timedelta(microseconds=100), now - timedelta(microseconds=100))])
        self.assertEqual(t.parse("time < '2013-08-13'"),
                         [DateRange(epoch, datetime(2013, 8, 13))])
        self.assertEqual(t.parse("time < 2013-08-13"),
                         [DateRange(epoch, datetime(2013, 8, 13))])
        self.assertEqual(t.parse("time > '2013-08-12 23:32:01.232'"),
                         [DateRange(datetime(2013, 8, 12, 23, 32, 1, 232000), now)])
        self.assertEqual(t.parse("time > '2013-08-12' and time < '2013-08-13'"),
                         [DateRange(datetime(2013, 8, 12), now), DateRange(epoch, datetime(2013, 8, 13))])
        self.assertEqual(t.parse("time > '2013-08-12 23:32:01.232' and time < '2013-08-13'"),
                         [DateRange(datetime(2013, 8, 12, 23, 32, 1, 232000), now),
                          DateRange(epoch, datetime(2013, 8, 13))])
        self.assertEqual(t.parse("time > '2013-08-12 23:32:01.232' and user = 'foo'"),
                         [DateRange(datetime(2013, 8, 12, 23, 32, 1, 232000), now)])
        self.assertEqual(t.parse("time > '2013-08-12 23:32:01.232' and user = 'foo' and time < '2013-08-13'"),
                         [DateRange(datetime(2013, 8, 12, 23, 32, 1, 232000), now),
                          DateRange(epoch, datetime(2013, 8, 13))])
        self.assertEqual(t.parse("time > 1388534400"), [DateRange(datetime.fromtimestamp(1388534400), now)])
        self.assertEqual(t.parse("time > 1388534400s"), [DateRange(datetime.fromtimestamp(1388534400), now)])
        self.assertEqual(t.parse("time = 1388534400s"),
                         [DateRange(datetime.fromtimestamp(1388534400), datetime.fromtimestamp(1388534400))])
        self.assertEqual(t.parse("time = 1388534400s"),
                         [DateRange(datetime.fromtimestamp(1388534400), datetime.fromtimestamp(1388534400))])
        self.assertEqual(t.parse("time = 1400497861762723"),
                         [DateRange(datetime.fromtimestamp(1400497861), datetime.fromtimestamp(1400497861))])
