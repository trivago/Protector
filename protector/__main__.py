import logging
import sys
import daemonocle
import os

from protector.daemon import ProtectorDaemon
from protector.config import loader
from protector.protector_main import Protector

__title__ = 'protector'
__author__ = 'Matthias Endler'
__license__ = 'BSD-3'
__copyright__ = 'Copyright 2016, trivago GmbH under BSD-3'


def main():
    """
    Setup consumer
    """
    config = loader.load_config()
    if config.version:
        show_version()
    if config.show_rules:
        show_rules()
    if not config.configfile and not (hasattr(config, "status") or hasattr(config, "stop")):
        show_configfile_warning()

    # Check if we have permissions to open the log file.
    check_write_permissions(config.logfile)
    start_proxy(config)


def check_write_permissions(file):
    """
    Check if we can write to the given file

    Otherwise since we might detach the process to run in the background
    we might never find out that writing failed and get an ugly
    exit message on startup. For example:
    ERROR: Child exited immediately with non-zero exit code 127

    So we catch this error upfront and print a nicer error message
    with a hint on how to fix it.
    """
    try:
        open(file, 'a')
    except IOError:
        print("Can't open file {}. "
              "Please grant write permissions or change the path in your config".format(file))
        sys.exit(1)


def show_rules():
    """
    Show the list of available rules and quit
    :return:
    """
    from rules.loader import import_rules
    from rules.rule_list import all_rules
    rules = import_rules(all_rules)
    print("")
    for name, rule in rules.iteritems():
        heading = "{} (`{}`)".format(rule.description(), name)
        print("#### {} ####".format(heading))
        for line in rule.reason():
            print(line)
        print("")
    sys.exit(0)


def show_version():
    """
    Show program version an quit
    :return:
    """
    from version import __version__
    print("{} {}".format(__package__, __version__))
    sys.exit(0)


def show_configfile_warning():
    print("Please specify a config file to load, e.g.")
    print("--configfile config.yaml")
    sys.exit(0)


def shutdown(message, code):
    logging.info('Daemon is stopping')
    logging.debug(message)


def start_proxy(config):
    """
    Start the http proxy
    :param config:
    :return:
    """
    protector = Protector(config.rules, config.whitelist)
    protector_daemon = ProtectorDaemon(config=config, protector=protector)

    daemon = daemonocle.Daemon(
        pidfile=config.pidfile,
        detach=(not config.foreground),
        shutdown_callback=shutdown,
        worker=protector_daemon.run
    )
    daemon.do_action(config.command)


if __name__ == '__main__':
    main()
