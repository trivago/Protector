from influxdb.influxdb08 import InfluxDBClient
import random
from string import ascii_lowercase
from tqdm import tqdm
import math
import datetime


class DummyWriter(object):
    def __init__(self, host="localhost", port=8086, username="root", password="root", database="metrics"):
        self.client = InfluxDBClient(host, port, username, password, database)

    @staticmethod
    def create_datapoint(name, columns, points):
        """
        Create datastructure in InfluxDB 0.8 data format
        :param name:
        :param columns:
        :param points:
        :return:
        """
        return {
            "time_precision": "s",
            "name": name,
            "columns": columns,
            "points": points,
        }

    @staticmethod
    def dummy_seriesname():
        parts = []
        for num_parts in range(random.randint(3, 5)):
            parts.append(''.join(random.choice(ascii_lowercase) for _ in range(random.randint(5, 20))))
        return '.'.join(parts)

    def create_series(self, num_series, batch_size=5000):
        """
        Write one data point for each series name to initialize the series
        :param num_series: Number of different series names to create
        :param batch_size: Number of series to create at the same time
        :return:
        """
        datapoints = []
        for _ in range(num_series):
            name = self.dummy_seriesname()
            datapoints.append(self.create_datapoint(name, ["value"], [[1]]))
        for data in tqdm(self.batch(datapoints, batch_size)):
            self.client.write_points(data)

    @staticmethod
    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]

    def write_points(self, series_name, start_date, end_date, resolution=10, batch_size=5000):
        """
        Create sample datapoints between two dates with the given resolution (in seconds)
        :param series_name:
        :param start_date:
        :param end_date:
        :param resolution:
        :param batch_size:
        """
        start_ts = int(start_date.strftime("%s"))
        end_ts = int(end_date.strftime("%s"))

        range_seconds = end_ts - start_ts
        num_datapoints = range_seconds / resolution

        timestamps = [start_ts + i * resolution for i in range(num_datapoints)]

        columns = ["time", "value"]
        for batch in tqdm(self.batch(timestamps, batch_size)):
            points = []
            for timestamp in batch:
                point = random.randint(1, 100)
                points.append([timestamp, point])
            datapoint = self.create_datapoint(series_name, columns, points)
            self.client.write_points([datapoint])


if __name__ == "__main__":
    dummy_writer = DummyWriter(host="influxdb")
    print "Creating sample series"
    dummy_writer.create_series(1000)
    sample_series_name = 'datacenter.server.appname.metricname'
    print "Creating sample datapoints for series {}".format(sample_series_name)
    start_date = datetime.datetime.now() - datetime.timedelta(days=14)
    end_date = datetime.datetime.now()
    dummy_writer.write_points(sample_series_name, start_date, end_date, resolution=1)
