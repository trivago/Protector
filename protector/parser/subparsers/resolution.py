import re
from protector.influxdb.time_expression import TimeExpression
from protector.influxdb.resolution import Resolution


class ResolutionParser(object):
    """
    Calculate the data resolution from a query, which is
    the time interval between two data points.
    The resolution will always be converted to seconds.
    """

    # Regex pattern to extract the value and unit of a group by time() statement
    # E.g. group by time(10s) => { 'value': 10, 'unit': s }
    GROUP_BY_TIME_PATTERN = re.compile(r'\s*(?:by)?\s*time\((\d+)([wdhmsu]|ms)\).*')

    def __init__(self):
        pass

    def parse(self, group_by_stmt):
        """
        Extract the data resolution of a query in seconds
        E.g. "group by time(99s)" => 99

        :param group_by_stmt: A raw InfluxDB group by statement
        """
        if not group_by_stmt:
            return Resolution.MAX_RESOLUTION

        m = self.GROUP_BY_TIME_PATTERN.match(group_by_stmt)
        if not m:
            return None

        value = int(m.group(1))
        unit = m.group(2)
        resolution = self.convert_to_seconds(value, unit)

        # We can't have a higher resolution than the max resolution
        return max(resolution, Resolution.MAX_RESOLUTION)

    @staticmethod
    def convert_to_seconds(value, unit):
        if unit not in TimeExpression.UNIT_CONVERSION.keys():
            # Invalid query
            return None
        conversion = TimeExpression.UNIT_CONVERSION[unit]
        return value * conversion
