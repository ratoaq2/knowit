import locale
import os
import pickle
import typing

import pytest
from pymediainfo import MediaInfo

from knowit import know
from knowit.config import Config
from knowit.provider import ProviderError
from knowit.providers import mediainfo as mediainfo_module
from knowit.providers.mediainfo import (
    MediaInfoCliExecutor,
    MediaInfoCTypesExecutor,
    MediaInfoExecutor,
    MediaInfoProvider,
)
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


def _raise_open_error(filename: str, **kwargs: typing.Any) -> str:
    # What pymediainfo raises when libmediainfo cannot open an existing file (issue #200).
    raise RuntimeError(f'An error occured while opening {filename} with libmediainfo')


@pytest.mark.parametrize(
    'executor',
    [
        pytest.param(MediaInfoCTypesExecutor('libmediainfo.so.0', (23, 11)), id='ctypes'),
        pytest.param(MediaInfoCliExecutor('mediainfo', (24, 1)), id='cli'),
    ],
)
def test_mediainfo_open_error_raises_provider_error(
    executor: MediaInfoExecutor, monkeypatch: pytest.MonkeyPatch, config: Config
) -> None:
    # Given: under a C locale, libmediainfo cannot open a non-ascii name.
    # The library raises RuntimeError. The cli prints "media": null and exits with 0.
    monkeypatch.setattr(MediaInfo, 'parse', _raise_open_error)
    monkeypatch.setattr(mediainfo_module, 'run_command', lambda args: '{"media": null}')
    monkeypatch.setattr(MediaInfoExecutor, 'get_executor_instance', lambda suggested_path=None: executor)
    provider = MediaInfoProvider(config, None)

    # When
    with pytest.raises(ProviderError) as error:
        provider.describe('/video/Everyone’s Dignity.mkv', {})

    # Then
    assert 'Everyone’s Dignity.mkv' in str(error.value)


@pytest.mark.parametrize(
    ('filename', 'ctype', 'hint'),
    [
        pytest.param('Everyone’s Dignity.mkv', 'C', True, id='non-ascii-c-locale'),
        pytest.param('Everyone’s Dignity.mkv', 'C.UTF-8', False, id='non-ascii-utf8-locale'),
        pytest.param('ascii.mkv', 'C', False, id='ascii-c-locale'),
    ],
)
def test_mediainfo_open_error_locale_hint(
    filename: str, ctype: str, hint: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given
    monkeypatch.setattr(os, 'name', 'posix')
    monkeypatch.setattr(locale, 'setlocale', lambda category: ctype)

    # When
    error = mediainfo_module.open_error(filename)

    # Then
    assert ('Set LANG=C.UTF-8' in str(error)) is hint
