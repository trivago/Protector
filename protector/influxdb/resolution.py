class Resolution(object):
    # Many metrics collectors like collectd send metrics every 10s
    # so we use this as an estimate for the maximum data resolution
    MAX_RESOLUTION = 10
