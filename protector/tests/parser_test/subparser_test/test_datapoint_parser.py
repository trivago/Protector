import unittest

from protector.parser.subparsers.datapoints import DatapointsParser


class TestParseDatapoints(unittest.TestCase):
    def test_datapoints(self):
        d = DatapointsParser()
        self.assertEqual(d.parse(None, None, None), 0)
        self.assertEqual(d.parse(100, 10, None), 10)
        self.assertEqual(d.parse(1000, 100, None), 10)
        self.assertEqual(d.parse(1000, 100, 10), 10)
        self.assertEqual(d.parse(10000, 10, 10), 10)
        self.assertEqual(d.parse(10000, 10, None), 1000)
        self.assertEqual(d.parse(1, 10, None), 0)
        self.assertEqual(d.parse(10, 10, None), 1)
        self.assertEqual(d.parse(10, 10, 10000), 1)
        self.assertEqual(d.parse(-10000, 10, None), 0)
        self.assertIsNone(d.parse(10000, -10, None))
