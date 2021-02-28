# -*- coding: utf-8 -*-

import pytest

from knowit import know

from . import (
    assert_expected,
    id_func,
    mediafiles
)


@pytest.mark.parametrize('media', mediafiles.get_json_media('ffmpeg'), ids=id_func)
def test_ffmpeg_provider(ffmpeg, media, options):
    # Given
    ffmpeg[media.video_path] = media.input_data

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)


@pytest.mark.parametrize('media', mediafiles.get_real_media('ffmpeg'), ids=id_func)
def test_ffmpeg_provider_real_media(media, options):
    # Given
    options['provider'] = 'ffmpeg'

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
