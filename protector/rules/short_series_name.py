from result import Ok, Err

from protector.influxdb.keyword import Keyword
from protector.rules.rule import Rule


class RuleChecker(Rule):
    def __init__(self):
        # Todo: Make this configurable in config file
        self.min_series_name_length = 11

    @staticmethod
    def description():
        return "Prevent queries for short series names"

    @staticmethod
    def reason():
        return ["The shorter the regex for the series name, the more series names get potentially matched.",
                "This is a huge performance hit for InfluxDB."]

    def check(self, query):
        """
        :param query:
        """
        if query.get_type() in {Keyword.LIST, Keyword.DROP}:
            series = query.series_stmt
        else:
            series = query.from_stmt

        if len(series) >= self.min_series_name_length:
            return Ok(True)

        return Err("Series name too short. Please be more precise.")
