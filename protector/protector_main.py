import logging
from result import Ok, Err
import re

from protector.guard.guard import Guard
from protector.parser.query_parser import QueryParser
from protector.sanitizer.sanitizer import Sanitizer
from protector.influxdb.keyword import Keyword


class Protector(object):
    """
    The main protector class which checks for malicious queries
    """

    def __init__(self, rules, whitelist=[], safe_mode=True):
        """
        :param rules: A list of rules to evaluate
        :param safe_mode: If set to True, allow the query in case it can not be parsed
        :return:
        """
        self.parser = QueryParser()
        self.guard = Guard(rules)
        self.sanitizer = Sanitizer()
        self.whitelist = whitelist
        self.safe_mode = safe_mode

    def check(self, query_string):
        logging.debug("Checking {}".format(query_string))
        query_sanitized = self.sanitizer.sanitize(query_string)
        query = self.parser.parse(query_sanitized)
        if query:
            if self.is_whitelisted(query):
                return Ok(True)
            return self.guard.is_allowed(query)
        else:
            error_msg = "Could not parse query: '{}'".format(query_string)
            logging.info(error_msg)
            if self.safe_mode:
                return Ok(True)
            else:
                return Err(error_msg)

    def is_whitelisted(self, query):
        if query.get_type() in {Keyword.LIST, Keyword.DROP}:
            series = query.series_stmt
        else:
            series = query.from_stmt
        for pattern in self.whitelist:
            match = re.match(pattern, series)
            if match:
                return True
        return False
