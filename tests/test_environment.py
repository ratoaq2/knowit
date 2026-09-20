import os
import pathlib
import typing

from knowit import __version__, api
from knowit.environment import (
    RELEVANT_ENV_VARS,
    collect_environment,
    detect_installation,
    format_environment,
    format_section,
)


def test_collect_environment_has_every_section(options: dict[str, typing.Any]) -> None:
    # When
    environment = collect_environment(options)

    # Then
    assert set(environment) == {'knowit', 'python', 'locale', 'providers'}


def test_collect_environment_reports_knowit_location() -> None:
    # When
    section = collect_environment()['knowit']

    # Then
    assert section['version'] == __version__
    assert os.path.isdir(section['location'])
    assert section['installation'] in (
        'site-packages',
        'source checkout',
        'vendored (bundled by another application)',
        'unknown',
    )


def test_collect_environment_reports_encodings() -> None:
    # When
    section = collect_environment()['locale']

    # Then
    assert section['filesystem_encoding']
    assert section['default_encoding']
    for name in RELEVANT_ENV_VARS:
        assert name in section


def test_collect_environment_reports_every_provider() -> None:
    # When
    section = collect_environment()['providers']

    # Then
    assert set(section) == set(api.provider_names)


def test_detect_installation_source_checkout(tmp_path: pathlib.Path) -> None:
    # Given
    package_dir = tmp_path / 'knowit'
    package_dir.mkdir()
    (tmp_path / 'pyproject.toml').write_text('', encoding='utf-8')

    # Then
    assert detect_installation(str(package_dir)) == 'source checkout'


def test_detect_installation_vendored(tmp_path: pathlib.Path) -> None:
    # Given
    package_dir = tmp_path / 'libs' / 'knowit'
    package_dir.mkdir(parents=True)

    # Then
    assert detect_installation(str(package_dir)) == 'vendored (bundled by another application)'


def test_format_section_renders_nested_values() -> None:
    # When
    lines = format_section('providers', {'ffmpeg': {'/usr/bin/ffprobe': 'v6.1.2'}, 'enzyme': 'not found'})

    # Then
    assert lines == [
        'providers:',
        '  ffmpeg:',
        '    /usr/bin/ffprobe: v6.1.2',
        '  enzyme: not found',
    ]


def test_format_environment_does_not_truncate_long_values() -> None:
    # Given
    location = '/a/very/long/path/that/is/clearly/longer/than/fifty/two/characters/libmediainfo.so.0'
    environment = {'providers': {'mediainfo': {location: 'v25.9'}}}

    # When
    output = format_environment(environment)

    # Then
    assert location in output


def test_debug_info_keeps_full_values(options: dict[str, typing.Any]) -> None:
    # When
    output = api.debug_info(options)

    # Then
    assert f'KnowIt {__version__}' in output
    assert 'filesystem_encoding' in output
    assert api.__name__  # module imported correctly
