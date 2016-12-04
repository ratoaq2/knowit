# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from datetime import timedelta

import pytest
from six import text_type
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode

import knowit


duration_re = re.compile(r'(?P<hours>\d{1,2}):'
                         r'(?P<minutes>\d{1,2}):'
                         r'(?P<seconds>\d{1,2})(?:\.'
                         r'(?P<millis>\d{3})'
                         r'(?P<micro>\d{3})?\d*)?')


def construct_mapping(self, node, deep=False):
    if not isinstance(node, MappingNode):
        raise ConstructorError(None, None,
                               "expected a mapping node, but found %s" % node.id,
                               node.start_mark)
    mapping = {}
    for key_node, value_node in node.value:
        key = self.construct_object(key_node, deep=deep)
        try:
            hash(key)
        except TypeError as exc:
            raise ConstructorError("while constructing a mapping", node.start_mark,
                                   "found unacceptable key (%s)" % exc, key_node.start_mark)
        if key != 'duration':
            value = self.construct_object(value_node, deep=deep)
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


knowit.utils.CustomLoader.add_constructor(u'tag:yaml.org,2002:map', construct_mapping)


@pytest.fixture
def video_path(tmpdir):
    return text_type(tmpdir.ensure('video.mkv'))
