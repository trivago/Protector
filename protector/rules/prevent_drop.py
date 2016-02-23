from result import Ok, Err

from protector.influxdb.keyword import Keyword
from protector.rules.rule import Rule


class RuleChecker(Rule):
    @staticmethod
    def description():
        return "Prevent drop queries"

    @staticmethod
    def reason():
        return ["Drop queries mean data loss. This is a risky operation that should be restricted to admin users"]

    def check(self, query):
        """
        :param query:
        """
        if query.get_type() != Keyword.DROP:
            return Ok(True)

        return Err("Drop queries are forbidden as they mean data loss.")
