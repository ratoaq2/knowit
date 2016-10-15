from __future__ import unicode_literals

import json
import os
import sys
from argparse import ArgumentParser

from six import text_type

from . import api


def build_argument_parser():
    """Build the argument parser.

    :return: the argument parser
    :rtype: ArgumentParser
    """
    opts = ArgumentParser()
    opts.add_argument(dest='filepath', help='Path to the file to introspect', nargs='*')

    provider_opts = opts.add_argument_group('Providers')
    provider_opts.add_argument('-p', '--provider', dest='provider', default=None,
                               help='The provider to be used: enzyme or mediainfo.')

    return opts


def knowit(video_path, options):
    """Extract video metadata."""
    info = api.knowit(video_path, vars(options))
    print('For: {0}'.format(video_path))
    print(json.dumps(info, cls=StringEncoder, indent=4, ensure_ascii=False))


class StringEncoder(json.JSONEncoder):
    """String json encoder."""

    def default(self, o):
        """Convert properties to string."""
        return text_type(o)


def main(args):
    """Main function for entry point."""
    argument_parser = build_argument_parser()
    options = argument_parser.parse_args(args)

    paths = []
    if options.filepath:
        for filepath in options.filepath:
            if os.path.isfile(filepath):
                paths.append(filepath)

    if paths:
        for filepath in paths:
            knowit(filepath, options)
    else:
        argument_parser.print_help()


if __name__ == '__main__':
    main(sys.argv[1:])
