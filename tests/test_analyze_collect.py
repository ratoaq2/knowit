"""Tests for scripts/analyze_collect.py, which reads the output of `knowit --collect`."""

import copy
import importlib.util
import pathlib
import sys
import typing

import pytest

from knowit import api
from knowit.collect import COLLECT_VERSION, Writer
from tests import read_json

MEDIAINFO_RAW = read_json('tests/data/mediainfo/media_001.mkv.json')
FFMPEG_RAW = read_json('tests/data/ffmpeg/media_001.mkv.json')


def _load_script() -> typing.Any:
    """Load scripts/analyze_collect.py, which is a dev script and not part of the package."""
    script = pathlib.Path(__file__).parent.parent / 'scripts' / 'analyze_collect.py'
    spec = importlib.util.spec_from_file_location('analyze_collect', script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules['analyze_collect'] = module
    spec.loader.exec_module(module)
    return module


analyze = _load_script()


@pytest.fixture(autouse=True)
def providers() -> None:
    api.available_providers.clear()
    api.initialize({})


def _record(key: str, ffmpeg_raw: typing.Any = None) -> dict[str, typing.Any]:
    return {
        'key': key,
        'size': 1,
        'mtime': 1,
        'providers': {
            'mediainfo': {'status': 'ok', 'raw': copy.deepcopy(MEDIAINFO_RAW)},
            'ffmpeg': {'status': 'ok', 'raw': ffmpeg_raw or copy.deepcopy(FFMPEG_RAW)},
        },
    }


@pytest.fixture
def capture(tmp_path: pathlib.Path) -> str:
    ffmpeg_raw = copy.deepcopy(FFMPEG_RAW)
    # The profile gives the codec when it is known, so only the codec name is left.
    del ffmpeg_raw['streams'][1]['profile']
    ffmpeg_raw['streams'][1]['codec_name'] = 'unknown-codec'
    ffmpeg_raw['streams'][1]['channels'] = 2
    ffmpeg_raw['streams'][0]['side_data_list'] = [{'side_data_type': 'DOVI configuration record', 'dv_profile': 8}]
    output = str(tmp_path / 'library.jsonl.gz')
    with Writer(output, {'knowit_collect': COLLECT_VERSION}) as writer:
        writer.write(_record('aaaa'))
        writer.write(_record('bbbb', ffmpeg_raw))
    return output


def test_load_records_keeps_the_last_record_of_a_file(tmp_path: pathlib.Path) -> None:
    # Given
    output = str(tmp_path / 'library.jsonl')
    with Writer(output, {'knowit_collect': COLLECT_VERSION}) as writer:
        writer.write({'key': 'a', 'size': 1})
        writer.write({'key': 'a', 'size': 2})

    # Then
    assert analyze.load_records(output) == {'a': {'key': 'a', 'size': 2}}


def test_load_records_rejects_a_newer_format(tmp_path: pathlib.Path) -> None:
    # Given
    output = str(tmp_path / 'library.jsonl')
    with Writer(output, {'knowit_collect': COLLECT_VERSION + 1}):
        pass

    # Then
    with pytest.raises(SystemExit):
        analyze.load_records(output)


def test_find_unknown_counts_unknown_values(capture: str) -> None:
    # When
    counts, examples = analyze.find_unknown(analyze.load_records(capture))

    # Then
    item = ('ffmpeg', 'audio codec', 'unknown-codec')
    assert counts[item] == 1
    assert examples[item] == 'bbbb'


def test_find_disagreements_counts_different_values(capture: str) -> None:
    # When
    counts, examples = analyze.find_disagreements(analyze.load_records(capture))

    # Then
    fields = dict(counts.keys())
    assert 'audio.channels_count' in fields
    assert dict(fields['audio.channels_count']) == {'ffmpeg': '2', 'mediainfo': '8'}


def test_find_disagreements_takes_name_guesses_from_the_stored_parse() -> None:
    # Given the replay masks the track names, only the stored parse holds the guess from 'Brazilian'
    record = _record('aaaa')
    record['providers']['mediainfo']['parsed'] = {'audio': [{'language': 'pt-BR'}]}
    record['providers']['ffmpeg']['parsed'] = {'audio': [{'language': 'pt'}]}

    # When
    counts, examples = analyze.find_disagreements({'aaaa': record})

    # Then
    assert ('audio.language', (('ffmpeg', 'pt'), ('mediainfo', 'pt-BR'))) in counts


@pytest.mark.parametrize(
    ('path', 'expected'),
    [
        ('streams[].codec_name', True),
        ('streams[].disposition.forced', True),
        ('streams[].disposition.visual_impaired', False),
        ('streams[].side_data_list[].dv_profile', False),
    ],
)
def test_is_mapped_matches_the_end_of_the_path(path: str, expected: bool) -> None:
    # Then
    assert analyze.is_mapped(path, analyze.mapped_names('ffmpeg')) is expected


def test_find_unmapped_puts_player_fields_first(capture: str, capsys: pytest.CaptureFixture[str]) -> None:
    # When
    files, values = analyze.find_unmapped(analyze.load_records(capture))
    analyze.command_unmapped(analyze.load_records(capture), top=1000)

    # Then
    item = ('ffmpeg', 'streams[].side_data_list[].dv_profile')
    assert files[item] == 1
    assert values[item] == {'8': 1}
    assert ('ffmpeg', 'streams[].codec_name') not in files
    keyword_lines = [' * ' in line for line in capsys.readouterr().out.splitlines()]
    assert keyword_lines[0]
    assert keyword_lines == sorted(keyword_lines, reverse=True)


def test_export_writes_the_fixtures_of_one_file(capture: str, tmp_path: pathlib.Path) -> None:
    # Given
    data_root = tmp_path / 'data'

    # When
    code = analyze.main(['export', capture, 'bb', '--name', 'dv-example', '--data-root', str(data_root)])

    # Then
    assert code == 0
    assert sorted(path.name for path in data_root.rglob('*.json')) == ['dv-example.mkv.json', 'dv-example.mkv.json']


def test_export_refuses_an_unclear_key(capture: str, tmp_path: pathlib.Path) -> None:
    # Then
    assert analyze.main(['export', capture, 'x', '--name', 'none', '--data-root', str(tmp_path)]) == 1
