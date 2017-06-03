# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import timedelta

import pytest
from six import string_types, text_type
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode, SequenceNode

import knowit
from knowit.units import units

duration_re = re.compile(r'(?P<hours>\d{1,2}):'
                         r'(?P<minutes>\d{1,2}):'
                         r'(?P<seconds>\d{1,2})(?:\.'
                         r'(?P<millis>\d{3})'
                         r'(?P<micro>\d{3})?\d*)?')


def construct_mapping(self, node, deep=False):
    if not isinstance(node, MappingNode):
        raise ConstructorError(None, None, 'expected a mapping node, but found {0}'.format(node.id), node.start_mark)
    mapping = {}
    for key_node, value_node in node.value:
        key = self.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError as exc:
            raise ConstructorError('while constructing a mapping', node.start_mark,
                                   'found unacceptable key (%s)' % exc, key_node.start_mark)
        if key != 'duration':
            value = self.construct_object(value_node, deep=deep)
            value = parse_quantity(value)
        else:

            match = duration_re.match(value_node.value)
            if match:
                h, m, s, ms, mc = duration_re.match(value_node.value).groups('0')
                value = timedelta(hours=int(h), minutes=int(m), seconds=int(s),
                                  milliseconds=int(ms), microseconds=int(mc))
            else:
                value = self.construct_object(value_node, deep=deep)
        mapping[key] = value
    return mapping


def construct_sequence(self, node, deep=False):
    if not isinstance(node, SequenceNode):
        raise ConstructorError(None, None, 'expected a sequence node, but found {0}'.format(node.id), node.start_mark)
    sequence = []
    for value_node in node.value:
        value = self.construct_object(value_node, deep=deep)
        sequence.append(parse_quantity(value))

    return sequence


def parse_quantity(value):
    if isinstance(value, string_types):
        for unit in ('pixel', 'bit', 'byte', 'FPS', 'bps', 'Hz'):
            if value.endswith(' ' + unit):
                return units(value[:-(len(unit))] + ' * ' + unit)

    return value


knowit.utils.CustomLoader.add_constructor(u'tag:yaml.org,2002:map', construct_mapping)
knowit.utils.CustomLoader.add_constructor(u'tag:yaml.org,2002:seq', construct_sequence)


@pytest.fixture
def video_path(tmpdir):
    return text_type(tmpdir.ensure('video.mkv'))
