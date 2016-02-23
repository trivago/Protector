from collections import defaultdict
import logging

from protector.influxdb.keyword import Keyword
from protector.influxdb.resolution import Resolution
from protector.parser.subparsers.datapoints import DatapointsParser
from protector.parser.subparsers.resolution import ResolutionParser
from protector.parser.subparsers.time_range import TimeRangeParser
from protector.parser.subparsers.duration import DurationParser
from protector.query.select import SelectQuery
from protector.query.drop import DropQuery
from protector.query.delete import DeleteQuery
from protector.query.list import ListQuery


class QueryParser(object):
    def __init__(self):
        """
        Initialize query parsers and valid InfluxDB keywords
        """
        self.keywords = {
            Keyword.SELECT, Keyword.FROM, Keyword.WHERE,
            Keyword.LIMIT, Keyword.ORDER,
            Keyword.GROUP_BY, Keyword.DROP, Keyword.DELETE,
            Keyword.LIST, Keyword.SERIES
        }
        self.time_parser = TimeRangeParser()
        self.duration_parser = DurationParser()
        self.resolution_parser = ResolutionParser()
        self.datapoints_parser = DatapointsParser()

        self.parsed_time = None
        self.parsed_resolution = None
        self.parsed_datapoints = None
        self.parsed_time_overlap = None

    def parse(self, raw_query_string):
        """
        Parse a raw query string into fields
        :param raw_query_string: Raw InfluxDB query string
        """

        self._reset()

        if not isinstance(raw_query_string, basestring):
            return None

        query_string = self._cleanup(raw_query_string)
        parts = self._split(query_string)
        tokens = self._tokenize(parts)

        if tokens:
            # Run subparsers to analyze parts of the query
            self.parsed_resolution = self._parse_resolution(tokens)
            self.parsed_time = self._parse_time(tokens)
            self.parsed_time_overlap = self._parse_duration(self.parsed_time)
            self.parsed_datapoints = self._parse_datapoints(
                self.parsed_time_overlap.timespan_seconds(),
                self.parsed_resolution,
                self.parse_keyword(Keyword.LIMIT, tokens)
            )

        return self.create_query_object(tokens)

    @staticmethod
    def _cleanup(query):
        query = query.strip()
        if query.endswith(';'):
            query = query[:-1]
        return query

    @staticmethod
    def _split(query):
        """
        Split query strings into tokens
        :param query: A sanitized query string
        """
        return [word.strip() for word in query.split(' ')]

    def _tokenize(self, parts):
        current_keyword = None
        tokens = defaultdict(list)
        # The query type is defined as the first word in the query
        # (which should be a keyword)
        tokens['type'] = parts[0]
        for part in parts:
            if part in self.keywords:
                # New keyword
                current_keyword = part
            else:
                # Belongs to previous keyword
                if not current_keyword:
                    logging.warning("Invalid statement '%s'", ''.join(parts))
                    return None
                tokens[current_keyword] += [part]
        return tokens

    @staticmethod
    def parse_keyword(keyword, tokens):
        if not keyword or not tokens or keyword not in tokens:
            return None
        # Concatenate multiple tokens to one
        return ' '.join(tokens[keyword])

    @staticmethod
    def parse_group(tokens):
        if not tokens[Keyword.GROUP_BY]:
            return None
        group_stmt = tokens[Keyword.GROUP_BY]
        if len(group_stmt) < 2 or group_stmt[0] != 'by':
            logging.warning("Invalid group by statement: %s", group_stmt)
            return None
        return ' '.join(group_stmt[1:])

    def create_query_object(self, tokens):
        """
        Analyze query tokens and create an InfluxDBStatement from them
        Return None on error
        :param tokens: A list of InfluxDB query tokens
        """
        try:
            query_type = tokens['type']
            return getattr(self, 'create_%s_query' % query_type)(tokens)
        except (KeyError, TypeError):
            return self.invalid_query(tokens)

    def create_select_query(self, tokens):
        """
        Parse tokens of select query
        :param tokens: A list of InfluxDB query tokens
        """
        if not tokens[Keyword.SELECT]:
            return None
        if not tokens[Keyword.FROM]:
            return None

        return SelectQuery(
            self.parse_keyword(Keyword.SELECT, tokens),
            self.parse_keyword(Keyword.FROM, tokens),
            where_stmt=self.parse_keyword(Keyword.WHERE, tokens),
            limit_stmt=self.parse_keyword(Keyword.LIMIT, tokens),
            group_by_stmt=self.parse_group(tokens),
            duration=self.parsed_time_overlap.timespan_seconds(),
            resolution=self.parsed_resolution,
            time_ranges=self.parsed_time,
            time_overlap=self.parsed_time_overlap,
            datapoints=self.parsed_datapoints
        )

    def create_list_query(self, tokens):
        """
        Parse tokens of list query
        :param tokens: A list of InfluxDB query tokens
        """
        if not tokens[Keyword.SERIES]:
            # A list series keyword is allowed
            # without a series name or regex
            tokens[Keyword.SERIES] = ''
        return ListQuery(self.parse_keyword(Keyword.SERIES, tokens))

    def create_drop_query(self, tokens):
        """
        Parse tokens of drop query
        :param tokens: A list of InfluxDB query tokens
        """
        if not tokens[Keyword.SERIES]:
            return None
        return DropQuery(self.parse_keyword(Keyword.SERIES, tokens))

    def create_delete_query(self, tokens):
        """
        Parse tokens of delete query
        :param tokens: A list of InfluxDB query tokens
        """
        # From keyword is required
        if not tokens[Keyword.FROM]:
            return None
        where_stmt = self.parse_keyword(Keyword.WHERE, tokens)
        if where_stmt:
            if not where_stmt.startswith('time'):
                return None
        return DeleteQuery(
            self.parse_keyword(Keyword.FROM, tokens),
            self.parse_keyword(Keyword.WHERE, tokens)
        )

    @staticmethod
    def invalid_query(tokens):
        """
        Handler for invalid queries
        :param tokens: A list of InfluxDB query tokens
        """
        logging.warning("Unkown or invalid query.")
        try:
            logging.warning("The query was %s", ' '.join(tokens))
        except TypeError:
            pass
        return None

    def _parse_time(self, tokens):
        """
        Parse the date range for the query

        E.g. WHERE time > now() - 48h AND time < now() - 24h
        would result in DateRange(datetime_start, datetime_end)
        where
        datetime_start would be parsed from now() - 48h
        and
        datetime_end would be parsed from now() - 24h

        :param tokens:
        :return:
        """
        return self.time_parser.parse(self.parse_keyword(Keyword.WHERE, tokens))

    def _parse_resolution(self, tokens):
        """
        Parse resolution from the GROUP BY statement.
        E.g. GROUP BY time(10s) would mean a 10 second resolution
        :param tokens:
        :return:
        """
        return self.resolution_parser.parse(self.parse_keyword(Keyword.GROUP_BY, tokens))

    def _parse_duration(self, parsed_time):
        """
        Parse duration in seconds for the given query.
        The duration is parsed from the DateRange of the query.
        For example, consider the following query:
        select * from bla where time > now() - 2h
        The DateRange would be [now() - 2h, now()]
        Expressing this as seconds would be 2h => 2*60*60 seconds
        This would be the duration of the query.

        :param parsed_time:
        :return:
        """
        return self.duration_parser.parse(parsed_time)

    def _parse_datapoints(self, parsed_duration, parsed_resolution, limit):
        """
        Parse the number of datapoints of a query.
        This can be calculated from the given duration and resolution of the query.
        E.g. if the query has a duation of 2*60*60 = 7200 seconds and a resolution of 10 seconds
        then the number of datapoints would be 7200/10 => 7200 datapoints.

        :param parsed_duration:
        :param parsed_resolution:
        :param limit:
        :return:
        """
        return self.datapoints_parser.parse(parsed_duration, parsed_resolution, limit)

    def _reset(self):
        self.parsed_time = None
        self.parsed_resolution = Resolution.MAX_RESOLUTION
        self.parsed_duration = None
        self.parsed_datapoints = None
