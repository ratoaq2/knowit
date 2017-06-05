# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from knowit import know
from knowit.providers import MediaInfoProvider

from . import (
    Mock,
    assert_expected,
    parameters_from_yaml,
)


@pytest.mark.parametrize('expected,input', parameters_from_yaml(__name__, expected_key='expected', input_key='input'))
def test_mediainfo_provider(monkeypatch, video_path, expected, input):
    # Given
    options = dict(provider='mediainfo')
    parse_method = Mock()
    parse_method.to_data.return_value = input
    monkeypatch.setattr(MediaInfoProvider, 'native_lib', True)
    monkeypatch.setattr(MediaInfoProvider, '_parse', lambda self, video: parse_method)

    # When
    actual = know(video_path, options)

    # Then
    assert_expected(expected, actual)
