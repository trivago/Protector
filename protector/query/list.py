from query import Query
from protector.influxdb.keyword import Keyword


class ListQuery(Query):
    """
    Construct new InfluxDB list statement object
    """

    def __init__(self, series_stmt):
        super(ListQuery, self).__init__()
        self.set_type(Keyword.LIST)
        self.series_stmt = series_stmt

    def __str__(self):
        """
        Standard string representation of drop query
        """
        return ' '.join([Keyword.LIST.upper(), Keyword.SERIES.upper(), self.series_stmt])
