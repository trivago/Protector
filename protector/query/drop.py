from query import Query
from protector.influxdb.keyword import Keyword


class DropQuery(Query):
    """
    Construct new InfluxDB drop statement object
    """

    def __init__(self, series_stmt):
        super(DropQuery, self).__init__()
        self.set_type(Keyword.DROP)
        self.series_stmt = series_stmt

    def __str__(self):
        """
        Standard string representation of drop query
        """
        return ' '.join([Keyword.DROP.upper(), Keyword.SERIES.upper(), self.series_stmt])
