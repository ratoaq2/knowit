# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals

import re
import sys
from collections import Mapping
from datetime import timedelta
from pkg_resources import resource_exists, resource_isdir, resource_listdir, resource_stream
from six import string_types
import yaml
from yaml.constructor import Constructor

from knowit import serializer
from knowit.units import units

try:
    from mock import Mock
except ImportError:
    from unittest.mock import Mock


duration_re = re.compile(r'(?P<hours>\d{1,2}):'
                         r'(?P<minutes>\d{1,2}):'
                         r'(?P<seconds>\d{1,2})(?:\.'
                         r'(?P<millis>\d{3})'
                         r'(?P<micro>\d{3})?\d*)?')

serializer.YAMLLoader = serializer.get_yaml_loader({
    'tag:yaml.org,2002:str': lambda constructor, value: _parse_value(value),
    'tag:yaml.org,2002:seq': Constructor.construct_sequence,
})


def parameters_from_yaml(name, input_key=None, expected_key=None):
    package_name, resource_name = name.split('.', 1)

    resources = []
    if resource_isdir(package_name, resource_name):
        resources.extend([resource_name + '/' + r
                          for r in resource_listdir(package_name, resource_name) if r.endswith(('.yml', '.yaml'))])
    elif resource_exists(package_name, resource_name + '.yml'):
        resources.append(resource_name + '.yml')
    elif resource_exists(package_name, resource_name + '.yaml'):
        resources.append(resource_name + '.yaml')

    if not resources:
        raise RuntimeError('Not able to load any yaml file for {0}'.format(name))

    parameters = []
    for resource_name in resources:
        with resource_stream(package_name, resource_name) as stream:
            data = yaml.load(stream, Loader=serializer.YAMLLoader)

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


def _parse_value(node):
    def parse_duration(value):
        match = duration_re.match(value)
        if match:
            h, m, s, ms, mc = match.groups('0')
            return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms), microseconds=int(mc))
        return value

    def parse_quantity(value):
        if isinstance(value, string_types):
            for unit in ('pixel', 'bit', 'byte', 'FPS', 'bps', 'Hz'):
                if value.endswith(' ' + unit):
                    return units(value[:-(len(unit))] + ' * ' + unit)

        return value

    result = node.value
    for method in (parse_quantity, parse_duration):
        if result and isinstance(result, string_types):
            result = method(node.value)
    return result


def is_iterable(obj):
    return isinstance(obj, (tuple, list))


def check_equals(expected, actual, different, prefix=''):
    if isinstance(expected, Mapping):
        check_mapping_equals(expected, actual, different=different, prefix=prefix)
    elif is_iterable(expected):
        check_sequence_equals(expected, actual, different=different, prefix=prefix)
    elif expected != actual:
        different.append((prefix, expected, actual))


def check_sequence_equals(expected, actual, different, prefix=''):
    if not is_iterable(actual) or len(expected) != len(actual):
        different.append((prefix, expected, actual))
        return

    for i, expected_value in enumerate(expected):
        actual_value = actual[i]
        key = '{0}[{1}].'.format(prefix, i)
        check_equals(expected_value, actual_value, different=different, prefix=key)


def check_mapping_equals(expected, actual, different, prefix=''):
    if not isinstance(actual, Mapping):
        different.append(('', expected, actual))
        return

    for expected_key, expected_value in expected.items():
        if expected_key not in actual:
            different.append((prefix + expected_key, expected_value, None))
            continue

        actual_value = actual[expected_key]
        key = prefix + expected_key
        check_equals(expected_value, actual_value, different=different, prefix=key)

    for actual_key, actual_value in actual.items():
        if actual_key not in expected:
            different.append((prefix + actual_key, None, actual_value))
            continue


def assert_expected(expected, actual):
    different = []
    check_equals(expected, actual, different=different)
    for (key, expected, actual) in different:
        print('{0}: Expected {1} got {2}'.format(key, expected, actual), file=sys.stderr)

    assert not different
