import pickle
import typing

import pytest

from knowit import know

from . import JsonMedia, Media, assert_expected, id_func, mediafiles


@pytest.mark.parametrize('media', mediafiles.get_json_media('ffmpeg'), ids=id_func)
def test_ffmpeg_provider(ffmpeg: dict[str, typing.Any], media: JsonMedia, options: dict[str, typing.Any]) -> None:
    # Given
    ffmpeg[media.video_path] = media.input_data

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual


@pytest.mark.parametrize('media', mediafiles.get_real_media('ffmpeg'), ids=id_func)
def test_ffmpeg_provider_real_media(media: Media, options: dict[str, typing.Any]) -> None:
    # Given
    options['provider'] = 'ffmpeg'

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual
