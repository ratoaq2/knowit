import json
import os
import pathlib
import re
import sys
from collections.abc import Mapping
from datetime import timedelta
from io import BytesIO
from zipfile import ZipFile

import requests
import yaml
from yaml.constructor import Constructor

from knowit import serializer
from knowit.api import provider_names
from knowit.serializer import format_property
from knowit.units import units


YAML_EXTENSIONS = ('.yml', '.yaml')


duration_re = re.compile(r'(?P<hours>\d{1,2}):'
                         r'(?P<minutes>\d{1,2}):'
                         r'(?P<seconds>\d{1,2})(?:\.'
                         r'(?P<millis>\d{3})'
                         r'(?P<micro>\d{3})?\d*)?')

serializer.YAMLLoader = serializer.get_yaml_loader({
    'tag:yaml.org,2002:str': lambda constructor, value: _parse_value(value),
    'tag:yaml.org,2002:seq': Constructor.construct_sequence,
})


one_ms = timedelta(milliseconds=1)


def normalize_path(path: str):
    return os.fspath(pathlib.Path(path))


def parameters_from_yaml(name, input_key=None, expected_key=None):
    package_name, resource_name = name.split('.', 1)

    files = []
    for yaml_ext in YAML_EXTENSIONS:
        yaml_file = os.path.join(package_name, resource_name + yaml_ext)
        if os.path.isfile(yaml_file):
            files.append(yaml_file)
            break

    parameters = []
    for file_path in files:
        data = read_yaml(file_path)

        if input_key and expected_key:
            parameters.append((data[expected_key], data[input_key]))
            continue

        for root_key, root_value in data.items():
            if isinstance(root_value, Mapping):
                for expected, data_input in root_value.items():
                    for properties in data_input if isinstance(data_input, (tuple, list)) else [data_input]:
                        parameters.append((root_key, expected, properties))
            else:
                for properties in root_value if isinstance(root_value, (tuple, list)) else [root_value]:
                    parameters.append((root_key, properties))

    return parameters


def read_file(file_path):
    with open(file_path, 'r') as f:
        return f.read()


def read_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.load(f, Loader=serializer.YAMLLoader)


def read_json(file_path):
    with open(file_path, 'r') as f:
        return json.loads(f.read())


def id_func(param):
    return repr(param)


class MediaFiles(object):
    """Represent media files in test/data folder."""

    def __init__(self):
        """Initialize the object."""
        self.videos = MediaFiles._videos()
        self.datafiles = MediaFiles._provider_datafiles()

    @staticmethod
    def _videos():
        data_path = os.path.join('tests', 'data', 'videos')

        # download matroska test suite
        if not os.path.exists(data_path) or len(os.listdir(data_path)) != 8:
            r = requests.get('http://downloads.sourceforge.net/project/matroska/test_files/matroska_test_w1_1.zip')
            with ZipFile(BytesIO(r.content), 'r') as f:
                f.extractall(data_path, [m for m in f.namelist() if os.path.splitext(m)[1] == '.mkv'])

        # populate a dict with mkv files
        files = []
        for path in os.listdir(data_path):
            name, _ = os.path.splitext(path)
            files.append(os.path.join(data_path, path))

        return files

    @staticmethod
    def _provider_datafiles():
        datafiles = {}
        for provider in provider_names:
            files = []
            data_path = os.path.join('tests', 'data', provider)
            if not os.path.isdir(data_path):
                continue
            for path in os.listdir(data_path):
                if not path.lower().endswith(YAML_EXTENSIONS):
                    files.append(os.path.join(data_path, path))

            datafiles[provider] = files

        return datafiles

    def get_real_media(self, provider_name):
        """Return only real video files."""
        return [Media(f, provider_name) for f in self.videos]

    def get_xml_media(self, provider_name):
        """Return all videos metadata as xml."""
        return [XmlMedia(f, provider_name) for f in self.datafiles[provider_name]]

    def get_yaml_media(self, provider_name):
        """Return all videos metadata as yaml."""
        return [YamlMedia(f, provider_name) for f in self.datafiles[provider_name]]

    def get_json_media(self, provider_name):
        """Return all videos metadata as json."""
        return [JsonMedia(f, provider_name) for f in self.datafiles[provider_name]]


mediafiles = MediaFiles()


class Media(object):
    """Represent a media."""

    def __init__(self, file_path, provider_name):
        """Initialize the object."""
        self.file_path = file_path
        self.provider_name = provider_name

    @property
    def video_path(self):
        """Return the video path."""
        return self.file_path

    @property
    def expected_data(self):
        """Return the expected video metadata."""
        yaml_file = None
        yaml_folder = os.path.normpath(os.path.join(os.path.split(self.video_path)[0], os.pardir))
        for yaml_ext in YAML_EXTENSIONS:
            yaml_file = os.path.join(yaml_folder, self.provider_name, os.path.basename(self.video_path) + yaml_ext)
            if os.path.isfile(yaml_file):
                break

        if not yaml_file or not os.path.isfile(yaml_file):
            raise IOError('Unable to find expected file for {!r}', self.video_path)

        return read_yaml(yaml_file)

    def __repr__(self):
        """Return the media representation."""
        return '<{} [{}]>'.format(self.__class__.__name__, self.video_path)

    def __str__(self):
        """Return the media path."""
        return self.video_path


class DataMedia(Media):
    """Represent a video without the real file, only the video metadata."""

    @property
    def video_path(self):
        """Return the video path."""
        return os.path.splitext(self.file_path)[0]

    @property
    def expected_data(self):
        """Return the expected video metadata."""
        yaml_file = None
        for yaml_ext in YAML_EXTENSIONS:
            yaml_file = self.video_path + yaml_ext
            if os.path.isfile(yaml_file):
                break

        if not yaml_file or not os.path.isfile(yaml_file):
            raise IOError('Unable to find expected file for {!r}', self.video_path)

        return read_yaml(yaml_file)


class XmlMedia(DataMedia):
    """Represent a video without the real file, only the video metadata as xml."""

    @property
    def input_data(self):
        """Return the video metadata as xml."""
        return read_file(self.file_path)


class YamlMedia(DataMedia):
    """Represent a video without the real file, only the video metadata as yaml."""

    @property
    def input_data(self):
        """Return the video metadata as yaml."""
        return read_yaml(self.file_path)


class JsonMedia(DataMedia):
    """Represent a video without the real file, only the video metadata as json."""

    @property
    def input_data(self):
        """Return the video metadata as json."""
        return read_json(self.file_path)


def _parse_value(node):
    def parse_duration(value):
        match = duration_re.match(value)
        if match:
            h, m, s, ms, mc = match.groups('0')
            return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms), microseconds=int(mc))
        return value

    def parse_quantity(value):
        if isinstance(value, str):
            for unit in ('pixel', 'bit', 'byte', 'FPS', 'bps', 'Hz'):
                if value.endswith(' ' + unit):
                    return units(value[:-(len(unit))] + ' * ' + unit)

        return value

    result = node.value
    for method in (parse_quantity, parse_duration):
        if result and isinstance(result, str):
            result = method(node.value)
    return result


def is_iterable(obj):
    return isinstance(obj, (tuple, list))


def to_string(profile: str, value):
    formatted_value = format_property(profile, value)
    return str(formatted_value) if formatted_value is not None else None


def check_equals(expected, actual, different, options, prefix=''):
    if isinstance(expected, Mapping):
        check_mapping_equals(expected, actual, different=different, options=options, prefix=prefix)
    elif is_iterable(expected):
        check_sequence_equals(expected, actual, different=different, options=options, prefix=prefix)
    elif isinstance(expected, timedelta):
        check_timedelta_equals(expected, actual, different=different, prefix=prefix)
    elif to_string(options['profile'], expected) != to_string(options['profile'], actual):
        different.append((prefix, expected, actual))


def check_timedelta_equals(expected, actual, different, prefix=''):
    if not isinstance(actual, timedelta) or not (expected - one_ms) <= actual <= (expected + one_ms):
        different.append((prefix, expected, actual))


def check_sequence_equals(expected, actual, different, options, prefix=''):
    if not is_iterable(actual) or len(expected) != len(actual):
        different.append((prefix, expected, actual))
        return

    for i, expected_value in enumerate(expected):
        actual_value = actual[i]
        key = '{0}[{1}].'.format(prefix, i)
        check_equals(expected_value, actual_value, different=different, options=options, prefix=key)


def check_mapping_equals(expected, actual, different, options, prefix=''):
    if not isinstance(actual, Mapping):
        different.append(('', expected, actual))
        return

    for expected_key, expected_value in expected.items():
        if expected_key == 'media_type':
            continue

        if expected_key not in actual:
            different.append((prefix + expected_key, expected_value, None))
            continue

        actual_value = actual[expected_key]
        key = prefix + expected_key

        if expected_key == 'path':
            expected_value = normalize_path(expected_value)
            actual_value = normalize_path(actual_value)

        check_equals(expected_value, actual_value, different=different, options=options, prefix=key)

    for actual_key, actual_value in actual.items():
        if actual_key not in expected:
            different.append((prefix + actual_key, None, actual_value))
            continue


def assert_expected(expected, actual, options=None):
    version = None
    if 'provider' in actual:
        version = actual['provider']['version']
        del actual['provider']['version']

    different = []
    check_equals(expected, actual, different=different, options=options or {'profile': 'default'})
    for (key, expected, actual) in different:
        print('{0}: Expected {1} got {2}'.format(key, expected, actual), file=sys.stderr)

    if different and options and options['debug_data']:
        print(f'Version: {version}')
        print(options['debug_data']())

    assert not different
