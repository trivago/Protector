from query import Query
from protector.influxdb.keyword import Keyword


class DeleteQuery(Query):
    """
    Construct new InfluxDB delete statement object
    """

    def __init__(self, from_stmt, where_stmt=None):
        super(DeleteQuery, self).__init__()
        self.set_type(Keyword.DELETE)
        self.from_stmt = from_stmt
        self.where_stmt = where_stmt

    def __str__(self):
        """
        Standard string representation of delete query
        """
        statements = [Keyword.DELETE.upper(), Keyword.FROM.upper(), self.from_stmt]
        if self.where_stmt:
            statements.extend([Keyword.WHERE.upper(), self.where_stmt])
        return ' '.join(statements)
