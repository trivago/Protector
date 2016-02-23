from result import Ok, Err

from protector.influxdb.keyword import Keyword
from protector.rules.rule import Rule


class RuleChecker(Rule):
    @staticmethod
    def description():
        return "Prevent negative group by statements"

    @staticmethod
    def reason():
        return ["Negative group by statements lead to undefined behavior.",
                "They can even bring down the server. That's why they are forbidden."]

    def check(self, query):
        """
        :param query:
        """
        if query.get_type() not in {Keyword.SELECT}:
            # Bailing out for non select queries
            return Ok(True)

        if query.get_resolution() > 0:
            return Ok(True)

        return Err("Group by statements need a positive time value (e.g. time(10s))")
