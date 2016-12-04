# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import glob
import os

try:
    from mock import Mock
except:
    from unittest.mock import Mock

import pytest
import yaml

from knowit import know
from knowit.api import available_providers
from knowit.providers.mediainfo import MediaInfoProvider
from knowit.utils import CustomLoader

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _parameters():
    parameters = []
    input_dir = os.path.join(__location__, 'mediainfo')
    yml_files = [f for f in glob.glob(os.path.join(input_dir, '*.yml'))]

    for input_file in yml_files:
        with open(input_file, 'r') as stream:
            data = yaml.load(stream, Loader=CustomLoader)

        raw = data['input']
        expected = data['expected']
        parameters.append([raw, expected])

    return parameters


@pytest.mark.parametrize('raw,expected', _parameters())
def test_mediainfo_provider(monkeypatch, video_path, raw, expected):
    # Given
    options = dict(provider='mediainfo')
    parse_method = Mock()
    parse_method.to_data.return_value = raw
    monkeypatch.setattr(available_providers['mediainfo'], 'native_lib', True)
    monkeypatch.setattr(MediaInfoProvider, '_parse', lambda self, video: parse_method)

    # When
    actual = know(video_path, options)

    # Then
    assert expected == actual
