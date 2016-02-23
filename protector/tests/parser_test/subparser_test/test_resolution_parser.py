import unittest

from protector.parser.subparsers.resolution import ResolutionParser
from protector.influxdb.resolution import Resolution


class TestParseResolution(unittest.TestCase):
    def setUp(self):
        self.resolution_parser = ResolutionParser()

    def test_invalid_resolutions(self):
        self.assertIsNone(self.resolution_parser.parse('asdf'), None)
        self.assertIsNone(self.resolution_parser.parse('time(-1s)'), None)
        self.assertEqual(self.resolution_parser.parse(None), Resolution.MAX_RESOLUTION)
        self.assertEqual(self.resolution_parser.parse(''), Resolution.MAX_RESOLUTION)

    def test_too_small(self):
        self.assertEqual(self.resolution_parser.parse('time(1s)'), Resolution.MAX_RESOLUTION)
        self.assertEqual(self.resolution_parser.parse('time(1000u)'), Resolution.MAX_RESOLUTION)

    def test_normal_resolution(self):
        self.assertEqual(self.resolution_parser.parse('time(100s)'), 100)
        self.assertEqual(self.resolution_parser.parse('time(1h)'), 60 * 60)
        self.assertEqual(self.resolution_parser.parse('time(3h)'), 3 * 60 * 60)
        self.assertEqual(self.resolution_parser.parse('time(8d)'), 8 * 24 * 60 * 60)
        self.assertEqual(self.resolution_parser.parse('time(2w)'), 14 * 24 * 60 * 60)
