# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

from pymediainfo import MediaInfo
import pytest

from knowit import (
    api,
    know,
)
from knowit.providers.mediainfo import MediaInfoExecutor

from . import (
    Mock,
    assert_expected,
    parameters_from_yaml,
)


@pytest.mark.parametrize('expected,input', parameters_from_yaml(__name__, expected_key='expected', input_key='input'))
def test_mediainfo_provider(monkeypatch, video_path, expected, input):
    # Given
    api.available_providers.clear()
    options = {'provider': 'mediainfo'}
    expected['provider'] = 'libmediainfo.so.0'
    executor = MediaInfoExecutor(expected['provider'])
    obj = MediaInfo('<xml></xml>')
    get_executor = Mock()
    get_executor.return_value = executor
    monkeypatch.setattr(MediaInfoExecutor, 'get_executor_instance', get_executor)
    monkeypatch.setattr(executor, 'extract_info', lambda v: obj)
    monkeypatch.setattr(obj, 'to_data', lambda: input)
    container = os.path.splitext(video_path)[1][1:]
    size = os.path.getsize(video_path)

    # When
    actual = know(video_path, options)

    # Then
    assert video_path == actual.pop('path', None)
    assert container == actual.pop('container', None)
    assert size == actual.pop('size', None)
    assert_expected(expected, actual)
