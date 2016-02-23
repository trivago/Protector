import argparse


class SmartFormatter(argparse.HelpFormatter):
    """
    A formatter for agrparse that allows to insert newline in the help text?

    Usage:

    parser.add_argument('-g', choices=['a', 'b', 'g', 'd', 'e'], default='a',
    help="R|Some option, where\n"
         " a = alpha\n"
         " b = beta\n"
         " g = gamma\n"
         " d = delta\n"
         " e = epsilon")

    See http://stackoverflow.com/a/22157136/270334
    """

    def _split_lines(self, text, width):
        # this is the RawTextHelpFormatter._split_lines
        if text.startswith('R|'):
            return text[2:].splitlines()
        return argparse.HelpFormatter._split_lines(self, text, width)
