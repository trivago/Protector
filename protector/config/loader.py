import collections
import yaml
import logging
import argparse
import sys

from protector.config import default_config
from protector.config.object_view import ObjectView
from protector.config.smart_formatter import SmartFormatter


def load_config():
    """
    Load settings from default config and optionally
    overwrite with config file and commandline parameters
    (in that order).
    """
    # We start with the default config
    config = flatten(default_config.DEFAULT_CONFIG)

    # Read commandline arguments
    cli_config = flatten(parse_args())

    if "configfile" in cli_config:
        logging.info("Reading config file {}".format(cli_config['configfile']))
        configfile = parse_configfile(cli_config['configfile'])
        config = overwrite_config(config, configfile)

    # Parameters from commandline take precedence over all others
    config = overwrite_config(config, cli_config)

    # Set verbosity level
    if 'verbose' in config:
        if config['verbose'] == 1:
            logging.getLogger().setLevel(logging.INFO)
        elif config['verbose'] > 1:
            logging.getLogger().setLevel(logging.DEBUG)

    return ObjectView(config)


def overwrite_config(old_values, new_values):
    config = old_values.copy()
    config.update(new_values)
    return config


def parse_configfile(configfile):
    """
    Read settings from file
    :param configfile:
    """
    with open(configfile) as f:
        try:
            return yaml.safe_load(f)
        except Exception as e:
            logging.fatal("Could not load default config file: %s", e)
            exit(-1)


def flatten(d, parent_key='', sep='_'):
    """
    Flatten keys in a dictionary
    Example:
    flatten({'a': 1, 'c': {'a': 2, 'b': {'x': 5, 'y' : 10}}, 'd': [1, 2, 3]})
    => {'a': 1, 'c_a': 2, 'c_b_x': 5, 'd': [1, 2, 3], 'c_b_y': 10}
    :param d:  Dictionary to flatten
    :param sep: Separator between keys
    :param parent_key: Key to merge with
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def parse_args(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Protector - A circruit breaker for Time Series Databases',
                                     formatter_class=SmartFormatter)
    parser.add_argument('--host', type=str, default=argparse.SUPPRESS,
                        help='Hostname to bind to (default: localhost)')
    parser.add_argument('--port', type=int, default=argparse.SUPPRESS,
                        help='Port to bind to (default: 8888)')
    parser.add_argument('--backend_host', type=str, default=argparse.SUPPRESS,
                        help='Hostname of Time Series Database (default: localhost)')
    parser.add_argument('--backend_port', type=int, default=argparse.SUPPRESS,
                        help='Port of Time Series Database (default: 8086)')
    parser.add_argument('-c', '--configfile', type=str, default=argparse.SUPPRESS,
                        help='Configfile path (default: None)')
    parser.add_argument('-v', '--verbose', action='count', default=argparse.SUPPRESS,
                        help='Set verbosity level. Increase verbosity by adding a v: -v -vv -vvv (default: 0)')
    parser.add_argument('--show_rules', action='store_true',
                        help='Show a list of available rules and quit')
    parser.add_argument('-f', '--foreground', action='store_true',
                        help='Run in foreground. Don\'t daemonize on start.')
    parser.add_argument('--version', action='store_true',
                        help='Show version')
    # Set command for daemon. The default is "start".
    # nargs is required to make "start" optional (avoid getting "error: too few arguments" when parsing parameters)
    # See http://stackoverflow.com/a/4480202/270334
    parser.add_argument('command', default='start', nargs='?', choices=('start', 'stop', 'status', 'restart'),
                        help='R|One of the following options:\n'
                             'start: Start the daemon (default)\n'
                             'stop: Stop the daemon\n'
                             'status: Show current status\n'
                             'restart: Restart the daemon\n')
    cli_args = parser.parse_args(args)
    # Convert config from argparse Namespace to dict
    return vars(cli_args)
