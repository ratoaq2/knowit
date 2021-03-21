
from pymediainfo import MediaInfo
import pytest

from knowit import api
from knowit.config import Config
from knowit.providers import EnzymeProvider
from knowit.providers.ffmpeg import FFmpegCliExecutor, FFmpegExecutor
from knowit.providers.mediainfo import MediaInfoCTypesExecutor, MediaInfoCliExecutor, MediaInfoExecutor

try:
    from mock import Mock
except ImportError:
    from unittest.mock import Mock


@pytest.fixture
def context():
    return {
        'profile': 'default',
    }


@pytest.fixture
def config():
    return Config.build()


@pytest.fixture
def options():
    return {}


def setup_mediainfo(executor, monkeypatch, options):
    options['provider'] = 'mediainfo'
    api.available_providers.clear()
    get_executor = Mock()
    get_executor.return_value = executor
    monkeypatch.setattr(MediaInfoExecutor, 'get_executor_instance', get_executor)

    data = {}
    extract_info = executor.extract_info
    monkeypatch.setattr(executor, 'extract_info',
                        lambda filename: MediaInfo(data[filename]) if filename in data else extract_info(filename))
    return data


@pytest.fixture
def mediainfo_cli(monkeypatch, options):
    return setup_mediainfo(MediaInfoCliExecutor.create(), monkeypatch, options)


@pytest.fixture
def mediainfo(monkeypatch, options):
    return setup_mediainfo(MediaInfoCTypesExecutor.create(), monkeypatch, options)


@pytest.fixture
def ffmpeg(monkeypatch, options):
    options['provider'] = 'ffmpeg'
    api.available_providers.clear()
    executor = FFmpegCliExecutor.create()
    get_executor = Mock()
    get_executor.return_value = executor
    monkeypatch.setattr(FFmpegExecutor, 'get_executor_instance', get_executor)

    data = {}
    extract_info = executor.extract_info
    monkeypatch.setattr(executor, 'extract_info',
                        lambda filename: data[filename] if filename in data else extract_info(filename))
    return data


@pytest.fixture
def enzyme(monkeypatch, options):
    options['provider'] = 'enzyme'

    data = {}
    extract_info = EnzymeProvider.extract_info
    monkeypatch.setattr(EnzymeProvider, 'extract_info',
                        lambda cls, filename: data[filename] if filename in data else extract_info(filename))

    return data
