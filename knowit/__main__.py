# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import logging
import sys
from argparse import ArgumentParser

from enzyme import __version__ as enzyme_version
from pymediainfo import __version__ as pymediainfo_version
from six import PY2
import yaml

from . import (
    __url__,
    __version__,
    api,
)
from .provider import ProviderError
from .serializer import (
    get_json_encoder,
    get_yaml_dumper,
)
from .utils import recurse_paths

logging.basicConfig(stream=sys.stdout, format='%(message)s')
logging.getLogger('CONSOLE').setLevel(logging.INFO)
logging.getLogger('knowit').setLevel(logging.ERROR)

console = logging.getLogger('CONSOLE')
logger = logging.getLogger('knowit')


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

    input_opts = opts.add_argument_group('Input')
    input_opts.add_argument('-E', '--fail-on-error', action='store_true', dest='fail_on_error', default=False,
                            help='Fail when errors are found on the media file.')

    output_opts = opts.add_argument_group('Output')
    output_opts.add_argument('-v', '--verbose', action='store_true', dest='verbose', default=False,
                             help='Display debug output')
    output_opts.add_argument('-r', '--raw', action='store_true', dest='raw', default=False,
                             help='Display raw properties')
    output_opts.add_argument('--report', action='store_true', dest='report', default=False,
                             help='Parse media and display report all non-detected values')
    output_opts.add_argument('-y', '--yaml', action='store_true', dest='yaml', default=False,
                             help='Display output in yaml format')
    output_opts.add_argument('-P', '--profile', dest='profile', default='default',
                             help='Display values according to specified profile: code, default, human, technical')

    conf_opts = opts.add_argument_group('Configuration')
    conf_opts.add_argument('-l', '--lib-location', dest='lib_location', default=None,
                           help='The location to search for native libraries')

    information_opts = opts.add_argument_group('Information')
    information_opts.add_argument('--version', dest='version', action='store_true', default=False,
                                  help='Display knowit version.')

    return opts


def knowit(video_path, options, context):
    """Extract video metadata."""
    context['path'] = video_path
    if not options.report:
        console.info('For: %s', video_path)
    else:
        console.info('Parsing: %s', video_path)
    info = api.know(video_path, context)
    if not options.report:
        console.info('Knowit %s found: ', __version__)
        console.info(dump(info, options, context))

    return info


def dump(info, options, context):
    """Convert info to string using json or yaml format."""
    if options.yaml:
        data = {info['path']: info} if 'path' in info else info
        result = yaml.dump(data, Dumper=get_yaml_dumper(context),
                           default_flow_style=False, allow_unicode=True)
        if PY2:
            result = result.decode('utf-8')

    else:
        result = json.dumps(info, cls=get_json_encoder(context), indent=4, ensure_ascii=False)

    return result


def main(args=None):
    """Execute main function for entry point."""
    argument_parser = build_argument_parser()
    args = args or sys.argv[1:]
    options = argument_parser.parse_args(args)

    if options.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger('enzyme').setLevel(logging.INFO)
    else:
        logger.setLevel(logging.WARNING)

    paths = recurse_paths(options.videopath)

    if paths:
        report = {}
        for i, videopath in enumerate(paths):
            try:
                context = dict(vars(options))
                if options.report:
                    context['report'] = report
                else:
                    del context['report']
                knowit(videopath, options, context)
            except ProviderError:
                logger.exception('Error when processing video')
            except OSError:
                logger.exception('OS error when processing video')
            except UnicodeError:
                logger.exception('Character encoding error when processing video')
            if options.report and i % 20 == 19 and report:
                console.info('Unknown values so far:')
                console.info(dump(report, options, vars(options)))

        if options.report:
            if report:
                console.info('Knowit %s found unknown values:', __version__)
                console.info(dump(report, options, vars(options)))
                console.info('Please report them at %s', __url__)
            else:
                console.info('Knowit %s knows everything. :-)', __version__)

    elif options.version:
        mi_location = api.available_providers['mediainfo'].native_lib
        if mi_location and hasattr(mi_location, '_name'):
            mi_location = getattr(mi_location, '_name')

        console.info('+-------------------------------------------------------+')
        console.info('|                   KnowIt %s %s |', __version__, (27 - len(__version__)) * ' ')
        console.info('+-------------------------------------------------------+')
        console.info('|                   Enzyme %s %s |', enzyme_version, (27 - len(enzyme_version)) * ' ')
        console.info('|                   pymediainfo %s %s |',
                     pymediainfo_version, (22 - len(pymediainfo_version)) * ' ')
        if not mi_location:
            console.info('|              MediaInfo not available                  |')
            console.info('|      https://mediaarea.net/en/MediaInfo/Download      |')
        else:
            mi_location = mi_location[-52:]
            spaces = max((53 - len(mi_location)), 0)
            console.info('|                   MediaInfo available                 |')
            console.info('| %s%s%s |', spaces / 2 * ' ', mi_location, (spaces / 2 + spaces % 2) * ' ')
        console.info('+-------------------------------------------------------+')
        console.info('|      Please report any bug or feature request at      |')
        console.info('|     https://github.com/ratoaq2/knowit/issues.         |')
        console.info('+-------------------------------------------------------+')
    else:
        argument_parser.print_help()


if __name__ == '__main__':
    main(sys.argv[1:])
