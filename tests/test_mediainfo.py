import pickle
import typing

import pytest

from knowit import know
from tests import JsonMedia, Media, mediafiles

from . import assert_expected, id_func


@pytest.mark.parametrize('media', mediafiles.get_json_media('mediainfo'), ids=id_func)
def test_mediainfo_provider(mediainfo: dict[str, typing.Any], media: JsonMedia, options: dict[str, typing.Any]) -> None:
    # Given
    mediainfo[media.video_path] = media.input_data

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual


@pytest.mark.parametrize('media', mediafiles.get_real_media('mediainfo'), ids=id_func)
def test_mediainfo_provider_real_media(media: Media, options: dict[str, typing.Any]) -> None:
    # Given
    options['provider'] = 'mediainfo'

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual


@pytest.mark.parametrize('media', mediafiles.get_real_media('mediainfo'), ids=id_func)
def test_mediainfo_provider_real_media_cli(
    mediainfo_cli: dict[str, typing.Any], media: Media, options: dict[str, typing.Any]
) -> None:
    # Given
    options['provider'] = 'mediainfo'

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual
