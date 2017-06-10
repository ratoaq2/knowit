# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from knowit import (
    api,
    know,
)
from knowit.providers.ffmpeg import FFmpegExecutor

from . import (
    Mock,
    assert_expected,
    parameters_from_yaml,
)


@pytest.mark.parametrize('expected,input', parameters_from_yaml(__name__, expected_key='expected', input_key='input'))
def test_mediainfo_provider(monkeypatch, video_path, expected, input):
    # Given
    api.available_providers.clear()
    options = {'provider': 'ffmpeg'}
    expected['provider'] = 'ffprobe'
    executor = FFmpegExecutor(expected['provider'])
    get_executor = Mock()
    get_executor.return_value = executor
    monkeypatch.setattr(FFmpegExecutor, 'get_executor_instance', get_executor)
    monkeypatch.setattr(executor, 'extract_info', lambda v: input)

    # When
    actual = know(video_path, options)

    # Then
    assert_expected(expected, actual)
