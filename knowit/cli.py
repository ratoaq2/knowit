# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import os
import sys
from argparse import ArgumentParser

from six import text_type

from . import VIDEO_EXTENSIONS, api


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
    print('For: {0}'.format(video_path))
    info = api.knowit(video_path, vars(options))
    if not options.no_output:
        print(json.dumps(info, cls=StringEncoder, indent=4, ensure_ascii=False))


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
        logging.basicConfig(stream=sys.stdout, format='%(message)s')
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('enzyme').setLevel(logging.WARNING)

    paths = []

    for candidate in options.videopath:
        if os.path.isfile(candidate):
            paths.append(candidate.decode(sys.getfilesystemencoding()))
        if os.path.isdir(candidate):
            for root, directories, filenames in os.walk(candidate):
                for filename in filenames:
                    if os.path.splitext(filename)[1] in VIDEO_EXTENSIONS:
                        fullpath = os.path.join(root, filename)
                        paths.append(fullpath.decode(sys.getfilesystemencoding()))

    if paths:
        for videopath in paths:
            knowit(videopath, options)
    else:
        argument_parser.print_help()


if __name__ == '__main__':
    main(sys.argv[1:])
