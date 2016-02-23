import re
import dateparser
from datetime import datetime, timedelta

from protector.influxdb.daterange import DateRange
from protector.influxdb.time_expression import TimeExpression


class TimeGrammar(object):
    """
    Grammars for time tokens
    The ordering is important because the first valid match is picked
    and matches can be subsets of others (e.g. datetimestr and timedelta)
    """
    TIME_STATEMENT = re.compile(r'time\s*([<=>])\s*(.*)')

    # InfluxDB keyword to separate time patterns
    KEYWORD_AND = 'and'

    # InfluxDB supports the following formats to specify time:
    # select * from series_name where time > '2013-08-12 23:32:01.232';
    # select * from series_name where time > now() - 1h;
    # select * from series_name where time > 1388534400s;
    # The patterns must be ordered by priority.
    TIME_PATTERNS = [
        # Match date strings in the format YYYY-MM-DD HH:MM:SS.mmm with HH:MM:SS.mmm being optional
        ('date_time', re.compile(r'\'?(\d{4}\-\d{2}\-\d{2}(\s\d{2}:\d{2}:\d{2}(\.\d{3})?)?)\'?\s*')),

        # Match relative time, e.g. now() - 2h, now() - 12w,...
        ('relative_time', re.compile(r'now\(\)\s*([+-])?\s*(\d+)([wdhmsu])?\s*')),

        # Unix timestamp format
        ('unix_time', re.compile(r'(\d+)s?\s*'))
    ]


class TimeRangeParser(object):
    """
    Creates a list of TimeExpression objects from InfluxDB time statements.
    Example:

    "time > now() - 2h" will create [ TimeExpressionBigger(datetime_obj)]
    """

    def __init__(self):
        self.epoch = TimeExpression.INFLUXDB_EPOCH

    def parse(self, where_stmt):
        if not where_stmt:
            return []
        return self.parse_time_expressions(where_stmt)

    def parse_time_expressions(self, where_stmt):
        raw_statements = self.split_statements(where_stmt)
        time_expressions = []
        for raw_statement in raw_statements:
            time_expression = self.parse_time_expression(raw_statement)
            if time_expression:
                time_expressions.append(time_expression)
        return time_expressions

    def parse_time_expression(self, raw_statement):
        match = TimeGrammar.TIME_STATEMENT.match(raw_statement)
        if not match:
            return
        comparison_operator = match.group(1)
        time_expression = match.group(2)
        return self.create_time_expression(comparison_operator, time_expression)

    def create_time_expression(self, comparison_operator, time_expression):
        for pattern_name, pattern in TimeGrammar.TIME_PATTERNS:
            match = pattern.match(time_expression)
            if match:
                datetime_obj = getattr(self, 'parse_%s' % pattern_name)(match)
                return self._create_time(comparison_operator, datetime_obj)

    @staticmethod
    def split_statements(raw_statements):
        return [stmt.strip() for stmt in raw_statements.split(TimeGrammar.KEYWORD_AND)]

    def parse_relative_time(self, match):
        sign, number, unit = match.groups()
        if sign:
            number = int(sign + number)
        # If no unit is given, the value is interpreted as microseconds.
        if not unit:
            unit = 'u'
        now = datetime.now()
        delta = self._create_timedelta(number, unit)
        return now + delta

    @staticmethod
    def _create_timedelta(value, unit):
        if unit not in TimeExpression.UNIT_NAMES.keys():
            # Invalid query
            return None
        params = {TimeExpression.UNIT_NAMES[unit]: value}
        return timedelta(**params)

    @staticmethod
    def parse_date_time(match):
        return dateparser.parse(match.group(1))

    @staticmethod
    def parse_unix_time(match):
        ts_string = match.group(1)
        # Truncate milliseconds
        ts = int(ts_string[:10])
        return datetime.fromtimestamp(ts)

    def _create_time(self, comparison_operator, datetime_obj):
        if comparison_operator == '=':
            return DateRange(datetime_obj, datetime_obj)
        elif comparison_operator == '>':
            return DateRange(datetime_obj, datetime.now())
        elif comparison_operator == '<':
            return DateRange(self.epoch, datetime_obj)
        else:
            # Invalid format
            return None
