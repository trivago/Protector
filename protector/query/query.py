class Query(object):
    """
    Common methods for working with InfluxDB Queries
    """

    def __init__(self):
        self.query_type = None

    def set_type(self, query_type):
        self.query_type = query_type

    def get_type(self):
        return self.query_type

    def get_resolution(self):
        """
        The resolution is the interval given in the the group_by field.
        (e.g. in the expression "group by time(10s)" it would be 10s)
        Only Select queries can have a resolution.
        All others don't, so we set this to None by default.
        """
        return None

    def get_duration(self):
        """
        The duration is the timespan to query data for.
        It can be set in the "where" clause.
        For instance, in the query:
        "select * from myseries where time > now() - 24h"
        the duration would be 24h.
        Durations can only be given in Select and Delete queries
        so we set this to None by default.
        """
        return None

    def get_datapoints(self):
        """
        Returns an estimate for the number datapoints that this query
        will return, where datapoints = duration * resolution
        Datapoints can only occur in Select and Delete queries
        so we set this to None by default.
        """
        return None
