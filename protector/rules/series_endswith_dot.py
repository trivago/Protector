from result import Ok, Err

from protector.influxdb.keyword import Keyword
from protector.rules.rule import Rule


class RuleChecker(Rule):
    @staticmethod
    def description():
        return "Prevent series names that end with a dot"

    @staticmethod
    def reason():
        return ["Such series usually indicate that the query is unfinished and ",
                "was executed by accident. To avoid the error, just remove the dot ",
                "or add another word (e.g. 'my.graphite.series.' -> 'my.graphite.series')"]

    def check(self, query):
        if query.get_type() in {Keyword.LIST, Keyword.DROP}:
            series = query.series_stmt
        else:
            series = query.from_stmt

        if not series.endswith('.') and not series.endswith('./'):
            return Ok(True)

        # Check that the dot was not escaped on purpose
        # Something like this would be fine: /my.awesome.series\./
        if series.endswith('\.') or series.endswith('\./'):
            return Ok(True)

        return Err("Query ends with dot. Was it executed by mistake? Add a word at the end or remove the dot.")
