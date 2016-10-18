# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import sys
from argparse import ArgumentParser

try:
    from scandir import walk
except ImportError:
    from os import walk

from six import text_type

from . import VIDEO_EXTENSIONS, api


logging.basicConfig(stream=sys.stdout, format='%(message)s')
logging.getLogger('CONSOLE').setLevel(logging.INFO)
logging.getLogger('knowit').setLevel(logging.ERROR)
logging.getLogger('enzyme').setLevel(logging.ERROR)

console = logging.getLogger('CONSOLE')


def build_argument_parser():
    """Build the argument parser.

    :return: the argument parser
    :rtype: ArgumentParser
    """
    opts = ArgumentParser()
    opts.add_argument(dest='videopath', help='Path to the video to introspect', nargs='*')

    provider_opts = opts.add_argument_group('Providers')
    provider_opts.add_argument('-p', '--provider', dest='provider', default=None,
                               help='The provider to be used: enzyme or mediainfo.')

    input_opts = opts.add_argument_group("Input")
    input_opts.add_argument('-E', '--fail-on-error', action='store_true', dest='fail_on_error', default=False,
                            help='Fail when errors are found on the media file.')

    output_opts = opts.add_argument_group("Output")
    output_opts.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                             help='Display debug output')
    output_opts.add_argument('-r', '--raw', action='store_true', dest='raw', default=False,
                             help='Display raw properties')
    output_opts.add_argument('-N', '--no-output', action='store_true', dest='no_output', default=False,
                             help='Do not display properties output')

    return opts


def knowit(video_path, options):
    """Extract video metadata."""
    console.info('For: %s', video_path)
    info = api.knowit(video_path, vars(options))
    if not options.no_output:
        console.info(json.dumps(info, cls=StringEncoder, indent=4, ensure_ascii=False))


class StringEncoder(json.JSONEncoder):
    """String json encoder."""

    def default(self, o):
        """Convert properties to string."""
        if hasattr(o, 'name'):
            return getattr(o, 'name')

        return text_type(o)


def main(args=None):
    """Main function for entry point."""
    argument_parser = build_argument_parser()
    args = args or sys.argv[1:]
    options = argument_parser.parse_args(args)

    if options.verbose:
        logging.getLogger('knowit').setLevel(logging.INFO)
        logging.getLogger('enzyme').setLevel(logging.WARNING)

    paths = []

    for path in options.videopath:
        if os.path.isfile(path):
            paths.append(path)
        if os.path.isdir(path):
            for root, directories, filenames in walk(path):
                for filename in filenames:
                    if os.path.splitext(filename)[1] in VIDEO_EXTENSIONS:
                        fullpath = os.path.join(root, filename)
                        paths.append(fullpath)

    if paths:
        encoding = 'utf-8' if os.name != 'nt' else sys.getfilesystemencoding()
        for videopath in paths:
            videopath = text_type(videopath, encoding)
            knowit(videopath, options)
    else:
        argument_parser.print_help()


if __name__ == '__main__':
    main(sys.argv[1:])
