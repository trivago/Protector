from result import Ok, Err

from protector.influxdb.keyword import Keyword
from protector.rules.rule import Rule
import datetime


class RuleChecker(Rule):
    def __init__(self):
        # Todo: Make this configurable from config file
        self.min_start_date = datetime.datetime.now() - datetime.timedelta(days=10)

    @staticmethod
    def description():
        return "Prevent querying for very old data"

    @staticmethod
    def reason():
        return ["Such queries can bring down the time series database",
                "because it needs to open and parse very old shards from disk"]

    def check(self, query):
        """
        :param query:
        """
        if query.get_type() not in {Keyword.SELECT}:
            # Only select queries need to be checked here
            # All others are not affected by this rule. Bailing out.
            return Ok(True)

        earliest_date = query.get_earliest_date()
        if earliest_date >= self.min_start_date:
            return Ok(True)

        return Err(("Querying for data before {} is prohibited. "
                    "Your beginning date is {}, which is before that.").format(self.min_start_date.strftime("%Y-%m-%d"),
                                                                              earliest_date))
