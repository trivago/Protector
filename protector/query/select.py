import datetime
from protector.query.query import Query
from protector.influxdb.keyword import Keyword
from protector.influxdb.time_expression import TimeExpression


class SelectQuery(Query):
    """
    Construct new InfluxDB select statement object
    """

    # QUERY KEYS
    OPTIONAL_KEY_WHERE_STMT = 'where_stmt'
    OPTIONAL_KEY_GROUP_BY_STMT = 'group_by_stmt'
    OPTIONAL_KEY_LIMIT_STMT = 'limit_stmt'
    OPTIONAL_KEY_RESOLUTION = 'resolution'
    OPTIONAL_KEY_DURATION = 'duration'

    # CALCULATED METADATA
    OPTIONAL_KEY_DATAPOINTS = 'datapoints'
    OPTIONAL_KEY_TIME_RANGES = 'time_ranges'  # All given time ranges in the query
    OPTIONAL_KEY_TIME_OVERLAP = 'time_overlap'  # The calculated overlap of all given time ranges in the query
    OPTIONAL_KEY_ORDER_BY_STMT = 'order_by'

    def __init__(self,
                 select_stmt,
                 from_stmt,
                 **kwargs):

        super(SelectQuery, self).__init__()
        # Required parameters
        self.set_type(Keyword.SELECT)
        self.select_stmt = select_stmt
        self.from_stmt = from_stmt

        # Optional parameters
        self.where_stmt = kwargs.get(self.OPTIONAL_KEY_WHERE_STMT, None)
        self.group_by_stmt = kwargs.get(self.OPTIONAL_KEY_GROUP_BY_STMT, None)
        self.limit_stmt = kwargs.get(self.OPTIONAL_KEY_LIMIT_STMT, None)
        self.order_by_stmt = kwargs.get(self.OPTIONAL_KEY_ORDER_BY_STMT, None)
        self.resolution = kwargs.get(self.OPTIONAL_KEY_RESOLUTION, None)
        self.duration = kwargs.get(self.OPTIONAL_KEY_DURATION, None)
        self.time_ranges = kwargs.get(self.OPTIONAL_KEY_TIME_RANGES, None)
        self.time_overlap = kwargs.get(self.OPTIONAL_KEY_TIME_OVERLAP, None)
        self.datapoints = kwargs.get(self.OPTIONAL_KEY_DATAPOINTS, None)

    def get_earliest_date(self):
        """
        Get the smallest date in the query
        E.g. in simple queries like select * from foo where time > now() - 24h
        this would be the date of yesterday
        This can be useful for checking if very old data is queried for example.
        :return:
        """
        if not self.time_overlap:
            return TimeExpression.INFLUXDB_EPOCH
        return self.time_overlap.start

    def get_latest_date(self):
        """
        Get the end date of the query
        E.g. in simple queries like select * from foo where time > now() - 24h
        this would be today
        :return:
        """
        if not self.time_overlap:
            return datetime.datetime.now()
        return self.time_overlap.end

    def get_resolution(self):
        return self.resolution

    def get_duration(self):
        return self.duration

    def get_datapoints(self):
        return self.datapoints

    def __str__(self):
        """
        Standard string representation of select query
        """
        # Required parameters
        statements = [
            (Keyword.SELECT, self.select_stmt),
            (Keyword.FROM, self.from_stmt)
        ]
        # Optional parameters
        if self.where_stmt:
            statements.append((Keyword.WHERE, self.where_stmt))
        if self.limit_stmt:
            statements.append((Keyword.LIMIT, self.limit_stmt))
        if self.group_by_stmt:
            statements.append((Keyword.GROUP_BY, ['by', self.group_by_stmt]))
        return self._format_statements(statements)

    def _format_statements(self, statements):
        lines = []
        for key, value in statements:
            lines.append(key.upper() + ' ' + self._concatenate_value(value))
        return ' '.join(lines)

    @staticmethod
    def _concatenate_value(value):
        if isinstance(value, basestring):
            return value
        # Concatenate multiple tokens to one
        return ' '.join(value)
