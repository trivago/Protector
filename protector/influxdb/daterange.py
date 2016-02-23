class DateRange(object):
    """
    A thin abstraction layer for date ranges
    """

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def timespan(self):
        return self.end - self.start

    def timespan_seconds(self):
        t = self.timespan()
        # A duration can never be negative
        return max(0, t.total_seconds())

    def __str__(self):
        return "Start: {}, End: {}, (Time span: {})".format(self.start, self.end, self.timespan())

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.start == other.start) and (self.end == other.end)
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)
