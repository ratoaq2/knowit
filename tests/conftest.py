import sys
import typing
from unittest.mock import Mock

import pytest

from knowit import api
from knowit.config import Config
from knowit.providers import EnzymeProvider
from knowit.providers.ffmpeg import FFmpegCliExecutor, FFmpegExecutor
from knowit.providers.mediainfo import MediaInfoCliExecutor, MediaInfoCTypesExecutor, MediaInfoExecutor
from knowit.providers.mkvmerge import MkvMergeCliExecutor, MkvMergeExecutor


@pytest.fixture
def context() -> dict[str, typing.Any]:
    return {
        'profile': 'default',
    }


@pytest.fixture
def config() -> Config:
    return Config.build()


@pytest.fixture
def options() -> dict[str, typing.Any]:
    return {'profile': 'code'}


@pytest.fixture
def home(tmp_path_factory: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> str:
    """Make a home folder with a user name in it, and install Python in it."""
    path = tmp_path_factory.mktemp('someone')
    python = path / 'venv' / 'bin' / 'python'
    python.parent.mkdir(parents=True)
    # platform.libc_ver() reads the executable.
    python.write_bytes(b'')
    monkeypatch.setenv('HOME', str(path))
    monkeypatch.setenv('USERPROFILE', str(path))
    monkeypatch.setattr(sys, 'executable', str(python))
    return str(path)


def setup_mediainfo(
    executor: MediaInfoExecutor | None,
    monkeypatch: pytest.MonkeyPatch,
    options: dict[str, typing.Any],
) -> dict[str, typing.Any]:
    assert executor
    options['provider'] = 'mediainfo'
    api.available_providers.clear()
    get_executor = Mock()
    get_executor.return_value = executor
    monkeypatch.setattr(MediaInfoExecutor, 'get_executor_instance', get_executor)

    data: dict[str, typing.Any] = {}
    extract_info = executor.extract_info
    monkeypatch.setattr(
        executor, 'extract_info', lambda filename: data[filename] if filename in data else extract_info(filename)
    )
    return data


@pytest.fixture
def mediainfo_cli(monkeypatch: pytest.MonkeyPatch, options: dict[str, typing.Any]) -> dict[str, typing.Any]:
    return setup_mediainfo(MediaInfoCliExecutor.create(), monkeypatch, options)


@pytest.fixture
def mediainfo(monkeypatch: pytest.MonkeyPatch, options: dict[str, typing.Any]) -> dict[str, typing.Any]:
    return setup_mediainfo(MediaInfoCTypesExecutor.create(), monkeypatch, options)


@pytest.fixture
def ffmpeg(monkeypatch: pytest.MonkeyPatch, options: dict[str, typing.Any]) -> dict[str, typing.Any]:
    options['provider'] = 'ffmpeg'
    api.available_providers.clear()
    executor = FFmpegCliExecutor.create()
    assert executor is not None
    get_executor = Mock()
    get_executor.return_value = executor
    monkeypatch.setattr(FFmpegExecutor, 'get_executor_instance', get_executor)

    data: dict[str, typing.Any] = {}
    extract_info = executor.extract_info
    monkeypatch.setattr(
        executor, 'extract_info', lambda filename: data[filename] if filename in data else extract_info(filename)
    )
    return data


@pytest.fixture
def mkvmerge(monkeypatch: pytest.MonkeyPatch, options: dict[str, typing.Any]) -> dict[str, typing.Any]:
    options['provider'] = 'mkvmerge'
    api.available_providers.clear()
    executor = MkvMergeCliExecutor.create()
    assert executor is not None
    get_executor = Mock()
    get_executor.return_value = executor
    monkeypatch.setattr(MkvMergeExecutor, 'get_executor_instance', get_executor)

    data: dict[str, typing.Any] = {}
    extract_info = executor.extract_info
    monkeypatch.setattr(
        executor, 'extract_info', lambda filename: data[filename] if filename in data else extract_info(filename)
    )
    return data


@pytest.fixture
def enzyme(monkeypatch: pytest.MonkeyPatch, options: dict[str, typing.Any]) -> dict[str, typing.Any]:
    options['provider'] = 'enzyme'

    data: dict[str, typing.Any] = {}
    extract_info = EnzymeProvider.extract_info
    monkeypatch.setattr(
        EnzymeProvider,
        'extract_info',
        lambda cls, filename: data[filename] if filename in data else extract_info(filename),
    )

    return data
