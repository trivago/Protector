from datetime import datetime
from protector.influxdb.daterange import DateRange
from protector.influxdb.time_expression import TimeExpression


class DurationParser(object):
    def __init__(self):
        pass

    def parse(self, time_ranges):
        if not time_ranges:
            # Get the biggest duration if nothing else is specified
            return DateRange(TimeExpression.INFLUXDB_EPOCH, datetime.now())

        # Calculate overlap of all time ranges.
        # Start with the first one
        overlap = time_ranges[0]
        for time_range in time_ranges:
            overlap = self.calculate_overlap(overlap, time_range)

        # Return the overlap as a date range and as the number of seconds
        return overlap

    @staticmethod
    def calculate_overlap(range1, range2):
        latest_start = max(range1.start, range2.start)
        earliest_end = min(range1.end, range2.end)
        overlap = DateRange(latest_start, earliest_end)
        return overlap
