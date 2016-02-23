from result import Ok, Err

from protector.influxdb.keyword import Keyword
from protector.rules.rule import Rule


class RuleChecker(Rule):
    @staticmethod
    def description():
        return "Prevent delete queries"

    @staticmethod
    def reason():
        return ["Deleting data can be a very expensive operation. This should not be done in InfluxDB 0.8 and before.",
                "See: https://influxdb.com/docs/v0.8/api/query_language.html#deleting-data-or-dropping-series"]

    def check(self, query):
        """
        :param query:
        """
        if query.get_type() != Keyword.DELETE:
            return Ok(True)

        return Err("Delete queries are forbidden.")
