"""Regression matrix for file names that have appeared in bug reports.

These names are the recurring subject of the issue tracker: superscripts, fractions,
typographic apostrophes, accents, brackets and non-latin scripts. None of them needs a
real media file, so they can run everywhere.
"""

import pathlib
import shutil
import tempfile
import typing

import pytest

from knowit import api
from knowit.pathcheck import (
    ADVERSARIAL_NAMES,
    CONTROL_NAME,
    MINIMAL_MKV,
    check_name,
    probe_name,
    verdict,
)


def _external_provider_loaded() -> bool:
    """Tell whether an external backend is installed."""
    loaded = api.loaded_providers({})
    return any(loaded.get(name) for name in ('mediainfo', 'ffmpeg', 'mkvmerge'))


needs_external_provider = pytest.mark.skipif(
    not _external_provider_loaded(),
    reason='needs mediainfo, ffprobe or mkvmerge installed',
)


def test_minimal_mkv_is_a_matroska_file() -> None:
    # Then
    assert MINIMAL_MKV.startswith(b'\x1a\x45\xdf\xa3')
    assert b'matroska' in MINIMAL_MKV
    assert b'A_PCM/INT/LIT' in MINIMAL_MKV


@needs_external_provider
def test_minimal_mkv_is_read_by_every_installed_provider(options: dict[str, typing.Any]) -> None:
    # Given a sample only some backends can read makes every verdict about them useless
    directory = tempfile.mkdtemp(prefix='knowit-sample-')
    options.pop('provider', None)
    try:
        # When
        result = probe_name(directory, CONTROL_NAME, MINIMAL_MKV, options)
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    # Then
    for provider_name, provider_result in result['providers'].items():
        assert provider_result['status'] in ('ok', 'not installed'), f'{provider_name}: {provider_result.get("error")}'


@pytest.mark.parametrize('name', ADVERSARIAL_NAMES, ids=ADVERSARIAL_NAMES)
def test_adversarial_name_can_be_written_and_read(name: str, tmp_path: pathlib.Path) -> None:
    # Given
    video_path = tmp_path / name

    # When
    video_path.write_bytes(MINIMAL_MKV)

    # Then
    assert video_path.is_file()
    assert video_path.read_bytes() == MINIMAL_MKV


@needs_external_provider
@pytest.mark.parametrize('name', ADVERSARIAL_NAMES, ids=ADVERSARIAL_NAMES)
def test_adversarial_name_is_accepted_by_the_api(
    name: str,
    tmp_path: pathlib.Path,
    options: dict[str, typing.Any],
) -> None:
    # Given
    video_path = tmp_path / name
    video_path.write_bytes(MINIMAL_MKV)
    options.pop('provider', None)

    # When knowit is asked about a file whose name holds unusual characters
    result = api.know(str(video_path), dict(options))

    # Then it answers instead of failing on the name
    assert result['path'] == str(video_path)


@pytest.mark.parametrize('name', ADVERSARIAL_NAMES, ids=ADVERSARIAL_NAMES)
def test_adversarial_name_behaves_like_the_control(
    name: str,
    tmp_path: pathlib.Path,
    options: dict[str, typing.Any],
) -> None:
    # Given the same bytes under a plain ascii name and under the name under test
    directory = str(tmp_path)
    options.pop('provider', None)
    control = probe_name(directory, CONTROL_NAME, MINIMAL_MKV, options)
    candidate = probe_name(directory, name, MINIMAL_MKV, options)

    # Then no provider fails only because of the name
    assert candidate['created'] is True
    for provider_name, message in verdict(control, candidate).items():
        assert 'the name is the problem' not in message, f'{provider_name}: {message}'


def test_check_name_reports_a_verdict_per_provider(options: dict[str, typing.Any]) -> None:
    # When
    result = check_name('The Accountant² (2025).mkv', options)

    # Then
    assert set(result['verdict']) == set(api.provider_names)
    assert result['candidate']['path']['non_ascii'] == ['U+00B2 SUPERSCRIPT TWO']


@needs_external_provider
def test_check_name_uses_the_given_file_when_there_is_one(options: dict[str, typing.Any]) -> None:
    # When
    result = check_name('café.mkv', options, source='tests/data/videos/test1.mkv')

    # Then
    assert result['sample'] == 'the file you provided'
    assert result['verdict']['mediainfo'].startswith('ok')


def test_verdict_separates_a_name_problem_from_a_file_problem() -> None:
    # Given
    control = {'created': True, 'providers': {'a': {'status': 'ok'}, 'b': {'status': 'error'}}}
    candidate = {'created': True, 'providers': {'a': {'status': 'error'}, 'b': {'status': 'error'}}}

    # Then
    assert verdict(control, candidate) == {
        'a': 'fails with this name only: the name is the problem',
        'b': 'fails with the control name too: the name is not the cause',
    }


def test_verdict_when_the_file_cannot_be_created() -> None:
    # Then
    assert verdict({}, {'created': False}) == {'*': 'the file could not be created with this name'}
