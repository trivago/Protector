import math

from protector.influxdb.resolution import Resolution


class DatapointsParser(object):
    def __init__(self):
        pass

    @staticmethod
    def parse(duration_seconds, resolution_seconds=Resolution.MAX_RESOLUTION, limit=None):
        """
        num_datapoints = min(duration/resolution, limit)

        :param duration_seconds: Time duration (in seconds) for which datapoints should be returned
        :param resolution_seconds: Time interval (in seconds) between data points
        :param limit: Maximum number of datapoints to return
        """

        if not duration_seconds or duration_seconds < 0:
            return 0

        if not resolution_seconds or resolution_seconds <= 0:
            return None

        num_datapoints = duration_seconds / resolution_seconds

        if limit:
            num_datapoints = min(int(limit), num_datapoints)

        return int(math.ceil(num_datapoints))
