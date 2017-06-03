# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os
import sys
from collections import OrderedDict
from datetime import timedelta

import babelfish
from six import PY2, string_types, text_type
import yaml

from knowit import VIDEO_EXTENSIONS
from knowit.units import format_quantity


def recurse_paths(paths):
    """Return a file system encoded list of videofiles.

    :param paths:
    :type paths: string or list
    :return:
    :rtype: list
    """
    enc_paths = []

    if isinstance(paths, (string_types, text_type)):
        paths = [p.strip() for p in paths.split(',')] if ',' in paths else paths.split()

    encoding = sys.getfilesystemencoding()
    for path in paths:
        if os.path.isfile(path):
            enc_paths.append(path.decode(encoding) if PY2 else path)
        if os.path.isdir(path):
            for root, directories, filenames in os.walk(path):
                for filename in filenames:
                    if os.path.splitext(filename)[1] in VIDEO_EXTENSIONS:
                        if PY2 and os.name == 'nt':
                            fullpath = os.path.join(root, filename.decode(encoding))
                        else:
                            fullpath = os.path.join(root, filename).decode(encoding)
                        enc_paths.append(fullpath)

    # Lets remove any dupes since mediainfo is rather slow.
    seen = set()
    seen_add = seen.add
    return [f for f in enc_paths if not (f in seen or seen_add(f))]


class StringEncoder(json.JSONEncoder):
    """String json encoder."""

    def default(self, o):
        """Convert properties to string."""
        if isinstance(o, babelfish.language.Language):
            return getattr(o, 'name')

        if hasattr(o, 'units'):
            return format_quantity(o)

        return text_type(o)


def todict(obj, classkey=None):
    """Transform an object to dict."""
    if isinstance(obj, string_types):
        return obj
    elif isinstance(obj, dict):
        data = {}
        for (k, v) in obj.items():
            data[k] = todict(v, classkey)
        return data
    elif hasattr(obj, '_ast'):
        return todict(obj._ast())
    elif hasattr(obj, '__iter__'):
        return [todict(v, classkey) for v in obj]
    elif hasattr(obj, '__dict__'):
        data = OrderedDict([(key, todict(value, classkey))
                            for key, value in obj.__dict__.items()
                            if not callable(value) and not key.startswith('_')])
        if classkey is not None and hasattr(obj, '__class__'):
            data[classkey] = obj.__class__.__name__
        return data
    return obj


class CustomDumper(yaml.SafeDumper):
    """Custom YAML Dumper."""

    pass


class CustomLoader(yaml.SafeLoader):
    """Custom YAML Loader."""

    pass


def default_representer(dumper, data):
    """Convert data to string."""
    return dumper.represent_str(str(data))


def ordered_dict_representer(dumper, data):
    """Representer for OrderedDict."""
    return dumper.represent_mapping('tag:yaml.org,2002:map', data.items())


CustomDumper.add_representer(OrderedDict, ordered_dict_representer)
CustomDumper.add_representer(babelfish.Language, default_representer)
CustomDumper.add_representer(timedelta, default_representer)
