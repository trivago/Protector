from datetime import datetime


class TimeExpression(object):
    # Smallest possible system date.
    # This is required for the calculation of the max duration between datetime objects.
    # We use the release day of InfluxDB 0.8 as the epoch
    # because it is the first official version supported by this tool.
    INFLUXDB_EPOCH = datetime.strptime('2014-08-22', "%Y-%m-%d")

    # Full names of all supported relative time units.
    # Useful for conversions of the internal InfluxDB format to the Python timedelta format.
    UNIT_NAMES = {
        'u': 'microseconds',
        's': 'seconds',
        'm': 'minutes',
        'h': 'hours',
        'd': 'days',
        'w': 'weeks'
    }

    # Conversions of all InfluxDB relative time units to seconds.
    # Useful for datapoint calculations.
    UNIT_CONVERSION = {'u': 0.001, 's': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800}
