import copy
import json
import os
import pathlib
import typing

import pytest

from knowit import collect
from knowit.__main__ import main
from knowit.collect import (
    COLLECT_VERSION,
    Writer,
    build_header,
    build_record,
    existing_parts,
    file_key,
    is_done,
    part_path,
    probe_frames,
    read_done,
    read_lines,
    read_part,
    run,
    strip_blobs,
)
from knowit.provider import ProviderError
from tests import read_json

MEDIAINFO_RAW = read_json('tests/data/mediainfo/media_001.mkv.json')
FFMPEG_RAW = read_json('tests/data/ffmpeg/media_001.mkv.json')


@pytest.fixture
def video(tmp_path: pathlib.Path) -> str:
    path = tmp_path / 'Some Movie (2024).mkv'
    path.write_bytes(b'\0' * 10)
    return str(path)


def test_file_key_does_not_disclose_the_path() -> None:
    # When
    key = file_key('/movies/Some Movie.mkv')

    # Then
    assert len(key) == 64
    assert 'Movie' not in key


def test_file_key_accepts_an_undecodable_name() -> None:
    # Given a name with a lone surrogate, as os.scandir gives for bytes that are not valid text
    name = '/movies/caf\udce9.mkv'

    # Then
    assert file_key(name) != file_key('/movies/café.mkv')


def test_strip_blobs_removes_binary_data_at_any_depth() -> None:
    # Given
    data = {'media': {'track': [{'@type': 'General', 'Cover_Data': 'AAAA', 'Format': 'Matroska'}]}}

    # When
    result = strip_blobs(data)

    # Then
    assert result == {'media': {'track': [{'@type': 'General', 'Format': 'Matroska'}]}}


def test_build_record_probes_the_selected_provider(
    mediainfo_cli: dict[str, typing.Any], options: dict[str, typing.Any], video: str
) -> None:
    # Given
    raw = copy.deepcopy(MEDIAINFO_RAW)
    raw['media']['track'][0]['Cover_Data'] = 'AAAA' * 1000
    mediainfo_cli[video] = raw

    # When
    record = build_record(video, options)

    # Then
    assert record['key'] == file_key(video)
    assert record['size'] == 10
    assert isinstance(record['mtime'], int)
    assert list(record['providers']) == ['mediainfo']
    result = record['providers']['mediainfo']
    assert result['status'] == 'ok'
    assert result['parsed']['video']
    assert result['seconds'] >= 0
    assert 'AAAA' not in json.dumps(result['raw'])


def test_build_record_masks_titles_and_path(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)

    # When
    record = build_record(video, options)

    # Then
    content = json.dumps(record, default=str)
    assert 'Super Title' not in content
    assert 'Some Movie' not in content
    assert record['providers']['ffmpeg']['status'] == 'ok'


def test_build_record_without_redaction_keeps_titles(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)

    # When
    record = build_record(video, options, anonymize=False)

    # Then
    assert 'Super Title' in json.dumps(record, default=str)


def test_build_record_probes_every_provider_by_default(options: dict[str, typing.Any], video: str) -> None:
    # Given no provider is selected
    options.pop('provider', None)

    # When
    record = build_record(video, options)

    # Then
    assert set(record['providers']) == {'mediainfo', 'ffmpeg', 'mkvmerge', 'enzyme'}
    for result in record['providers'].values():
        assert 'status' in result


@pytest.mark.parametrize(
    ('output', 'expected'),
    [
        ('library.jsonl.gz', 'library.part3.jsonl.gz'),
        ('library.jsonl', 'library.part3.jsonl'),
        ('library', 'library.part3'),
    ],
)
def test_part_path_numbers_the_parts(output: str, expected: str) -> None:
    # Then
    assert part_path(output, 1) == output
    assert part_path(output, 3) == expected


def test_build_header_describes_the_run(options: dict[str, typing.Any]) -> None:
    # When
    header = build_header(options, deep=True)

    # Then
    assert header['knowit_collect'] == COLLECT_VERSION
    assert header['providers'] == ['mediainfo', 'ffmpeg', 'mkvmerge', 'enzyme']
    assert header['deep'] is True
    assert set(header['dependencies']) >= {'mediainfo', 'ffmpeg', 'mkvmerge', 'enzyme'}
    assert 'environment' in header


@pytest.mark.parametrize('name', ['library.jsonl', 'library.jsonl.gz'])
def test_writer_writes_a_header_then_one_line_per_record(tmp_path: pathlib.Path, name: str) -> None:
    # Given
    output = str(tmp_path / name)

    # When
    with Writer(output, {'knowit_collect': COLLECT_VERSION}) as writer:
        writer.write({'key': 'a', 'title': 'café'})
        writer.write({'key': 'b'})

    # Then
    assert list(read_lines(output)) == [
        {'knowit_collect': COLLECT_VERSION},
        {'key': 'a', 'title': 'café'},
        {'key': 'b'},
    ]


def test_writer_starts_a_new_part_above_the_size_limit(tmp_path: pathlib.Path) -> None:
    # Given
    output = str(tmp_path / 'library.jsonl.gz')

    # When
    with Writer(output, {'knowit_collect': COLLECT_VERSION}, part_size=1) as writer:
        for key in 'abc':
            writer.write({'key': key})

    # Then
    parts = existing_parts(output)
    assert len(parts) == 3
    for part in parts:
        lines = list(read_part(part))
        assert lines[0] == {'knowit_collect': COLLECT_VERSION}
        assert len(lines) == 2


def test_writer_keeps_an_undecodable_name(tmp_path: pathlib.Path) -> None:
    # Given
    output = str(tmp_path / 'library.jsonl')

    # When
    with Writer(output, {}) as writer:
        writer.write({'name': 'caf\udce9.mkv'})

    # Then
    assert list(read_lines(output))[1] == {'name': 'caf\udce9.mkv'}


def test_read_lines_skips_a_damaged_last_line(tmp_path: pathlib.Path) -> None:
    # Given a run that stopped in the middle of a line
    output = tmp_path / 'library.jsonl'
    output.write_text('{"knowit_collect": 1}\n{"key": "a"}\n{"key": "b', encoding='utf-8')

    # Then
    assert list(read_lines(str(output))) == [{'knowit_collect': 1}, {'key': 'a'}]


def test_read_lines_skips_a_cut_gzip_part(tmp_path: pathlib.Path) -> None:
    # Given a gzip part that stopped before its end
    output = str(tmp_path / 'library.jsonl.gz')
    with Writer(output, {'knowit_collect': 1}) as writer:
        writer.write({'key': 'a'})
    content = pathlib.Path(output).read_bytes()
    pathlib.Path(output).write_bytes(content[:-8])

    # Then
    assert list(read_lines(output)) == [{'knowit_collect': 1}, {'key': 'a'}]


def test_resume_skips_an_unchanged_file_and_captures_a_changed_one(tmp_path: pathlib.Path, video: str) -> None:
    # Given an output that holds the file
    output = str(tmp_path / 'library.jsonl.gz')
    stat = os.stat(video)
    with Writer(output, {'knowit_collect': COLLECT_VERSION}) as writer:
        writer.write({'key': file_key(video), 'size': stat.st_size, 'mtime': stat.st_mtime_ns})

    # Then
    done = read_done(output)
    assert is_done(video, done)

    # When the file changes
    os.utime(video, ns=(stat.st_atime_ns, stat.st_mtime_ns + 10**9))

    # Then
    assert not is_done(video, done)


def test_resume_uses_the_last_line_of_a_key(tmp_path: pathlib.Path) -> None:
    # Given a file captured again in a second run
    output = str(tmp_path / 'library.jsonl')
    with Writer(output, {'knowit_collect': COLLECT_VERSION}) as writer:
        writer.write({'key': 'a', 'size': 1, 'mtime': 1})
    with Writer(output, {'knowit_collect': COLLECT_VERSION}) as writer:
        writer.write({'key': 'a', 'size': 2, 'mtime': 2})

    # Then
    assert existing_parts(output) == [output, str(tmp_path / 'library.part2.jsonl')]
    assert read_done(output) == {'a': (2, 2)}


def test_resume_ignores_a_missing_file() -> None:
    # Then
    assert not is_done('/does/not/exist.mkv', {})


def test_run_captures_new_files_and_skips_them_the_next_time(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str, tmp_path: pathlib.Path
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)
    output = str(tmp_path / 'library.jsonl.gz')

    # When
    first = run([video], output, dict(options))
    second = run([video], output, dict(options))

    # Then
    assert (first['captured'], first['skipped']) == (1, 0)
    assert (second['captured'], second['skipped']) == (0, 1)
    assert existing_parts(output) == [output]
    header, record = read_lines(output)
    assert header['knowit_collect'] == COLLECT_VERSION
    assert header['providers'] == ['ffmpeg']
    assert record['key'] == file_key(video)


def test_run_keeps_the_written_records_when_stopped(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str, tmp_path: pathlib.Path
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)
    output = str(tmp_path / 'library.jsonl.gz')

    def stop(index: int, video_path: str, status: str) -> None:
        raise KeyboardInterrupt

    # When
    summary = run([video, video], output, dict(options), on_file=stop)

    # Then
    assert summary['interrupted'] is True
    assert len(read_done(output)) == 1


def test_cli_collect_writes_the_output_and_a_summary(
    ffmpeg: dict[str, typing.Any], video: str, tmp_path: pathlib.Path, caplog: pytest.LogCaptureFixture
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)
    output = str(tmp_path / 'library.jsonl')

    # When
    with caplog.at_level('INFO', logger='CONSOLE'):
        main(['--collect', '-p', 'ffmpeg', '-o', output, video])

    # Then
    assert 'Files: 1, captured: 1, skipped (already in the output): 0' in caplog.text
    assert 'masked' in caplog.text
    assert len(read_done(output)) == 1
    assert 'Super Title' not in pathlib.Path(output).read_text(encoding='utf-8')


#: Frames in the ffprobe output format. The side data is written by hand: the test media has no HDR.
FRAMES_OUTPUT = json.dumps(
    {
        'frames': [
            {
                'media_type': 'video',
                'key_frame': 1,
                'pkt_pos': '5827',
                'pict_type': 'I',
                'side_data_list': [
                    {'side_data_type': 'Mastering display metadata', 'max_luminance': '10000000/10000'},
                    {'side_data_type': 'Content light level metadata', 'max_content': 1000, 'max_average': 400},
                    {'side_data_type': 'HDR Dynamic Metadata SMPTE2094-40 (HDR10+)', 'application_version': 1},
                    {'side_data_type': 'Dolby Vision RPU Data'},
                ],
            },
            {'media_type': 'video', 'key_frame': 0, 'pkt_pos': '10287', 'pict_type': 'B'},
        ]
    }
)


def test_probe_frames_keeps_only_the_side_data(monkeypatch: pytest.MonkeyPatch) -> None:
    # Given
    commands: list[list[str]] = []

    def fake_run_command(args: list[str]) -> str:
        commands.append(args)
        return FRAMES_OUTPUT

    monkeypatch.setattr(collect, 'run_command', fake_run_command)

    # When
    result = probe_frames('ffprobe', 'movie.mkv')

    # Then
    assert f'%+#{collect.DEEP_FRAMES}' in commands[0]
    assert commands[0][-1] == 'movie.mkv'
    first, second = result['frames']
    assert first['key_frame'] == 1
    assert [s['side_data_type'] for s in first['side_data_list']][2] == 'HDR Dynamic Metadata SMPTE2094-40 (HDR10+)'
    assert 'pkt_pos' not in first
    assert second == {'key_frame': 0, 'pict_type': 'B'}


def test_build_record_with_deep_adds_the_frames_to_ffmpeg(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)
    monkeypatch.setattr(collect, 'run_command', lambda args: FRAMES_OUTPUT)

    # When
    record = build_record(video, options, deep=True)

    # Then
    deep = record['providers']['ffmpeg']['deep']
    assert len(deep['frames']) == 2
    assert deep['seconds'] >= 0


def test_build_record_keeps_a_deep_probe_error(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)

    def failing_run_command(args: list[str]) -> str:
        raise ProviderError('ffprobe failed with exit status 1: Invalid data found')

    monkeypatch.setattr(collect, 'run_command', failing_run_command)

    # When
    record = build_record(video, options, deep=True)

    # Then
    result = record['providers']['ffmpeg']
    assert result['status'] == 'ok'
    assert result['deep'] == {'error': 'ProviderError: ffprobe failed with exit status 1: Invalid data found'}


def test_build_record_masks_the_path_in_a_deep_probe_error(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given ffprobe quotes the path in its error message
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)

    def failing_run_command(args: list[str]) -> str:
        raise ProviderError(f'ffprobe failed with exit status 1: {video}: Invalid data found')

    monkeypatch.setattr(collect, 'run_command', failing_run_command)

    # When
    record = build_record(video, options, deep=True)

    # Then
    error = record['providers']['ffmpeg']['deep']['error']
    assert 'Invalid data found' in error
    assert 'Some Movie' not in error
    assert os.path.dirname(video) not in error


def test_build_record_without_deep_has_no_frames(
    ffmpeg: dict[str, typing.Any], options: dict[str, typing.Any], video: str
) -> None:
    # Given
    ffmpeg[video] = copy.deepcopy(FFMPEG_RAW)

    # When
    record = build_record(video, options)

    # Then
    assert 'deep' not in record['providers']['ffmpeg']
