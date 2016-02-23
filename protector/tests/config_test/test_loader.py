import unittest
import os
import argparse
from mock import patch

from protector.config import loader


class Config:
    def __init__(self, configfile):
        self.configfile = configfile


class ParsedConfig:
    def __init__(self, kafka):
        self.kafka_host = kafka


class TestConfig(unittest.TestCase):
    def setUp(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.configfile = "{}/../fixtures/config_sample.yaml".format(path)

    def test_load_config(self):
        parsed_config = loader.parse_configfile(self.configfile)
        self.assertEqual(parsed_config["host"], "myhost")
        self.assertEqual(parsed_config["port"], 1234)

    def test_cli_overwrite(self):
        # Fake commandline arguments
        # Argparse returns a namespace, not a dictionary
        fake_args = argparse.Namespace()
        fake_args.host = "myhost"

        with patch('argparse.ArgumentParser.parse_args') as parse_args_mock:
            parse_args_mock.return_value = fake_args

            # Fake default config
            with patch('protector.config.default_config.DEFAULT_CONFIG') as default_config_mock:
                default_config_mock.return_value = {"host": "yourhost"}
                config = loader.load_config()

        # Check if the default setting got overwritten
        self.assertEqual(config.host, "myhost")

    def test_shorthand_cli_parameters(self):
        config = loader.parse_args([])
        self.assertIsNotNone(config)
        self.assertEqual(config['foreground'], False)
        config = loader.parse_args(['-f'])
        self.assertIsNotNone(config)
        self.assertEqual(config['foreground'], True)

    def test_overwrite_default_config(self):
        default_config_dict = {'kafka_host': 'defaulthost'}
        config = loader.overwrite_config(default_config_dict, {'kafka_host': 'otherhost'})
        self.assertEqual(config['kafka_host'], 'otherhost')
