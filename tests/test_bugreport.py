import pathlib
import typing

import yaml

from knowit import bugreport
from knowit.bugreport import (
    PARSED_SKIP_KEYS,
    PARSED_TEXT_KEYS,
    RAW_TEXT_KEYS,
    build_report,
    describe_path,
    dump_report,
    mask_text,
    redact,
)


def test_mask_text_hides_words_but_keeps_shape() -> None:
    # When
    masked = mask_text('The Accountant 2 (2025).mkv')

    # Then
    assert masked == 'xxx xxxxxxxxxx 0 (0000).xxx'


def test_mask_text_keeps_non_ascii_characters() -> None:
    # Given non-ascii characters are the subject of most path reports
    # When
    masked = mask_text('The Accountant² 33⅓ é')

    # Then
    assert masked == 'xxx xxxxxxxxxx² 00⅓ é'


def test_redact_masks_known_free_text_keys() -> None:
    # Given
    data = {'Title': 'Some Episode Name', 'Format': 'Matroska', 'Width': '1920'}

    # When
    result = redact(data, RAW_TEXT_KEYS)

    # Then
    assert result == {'Title': 'xxxx xxxxxxx xxxx', 'Format': 'Matroska', 'Width': '1920'}


def test_redact_is_case_insensitive() -> None:
    # When
    result = redact({'tags': {'TITLE': 'Episode', 'ENCODER': 'Lavf'}}, RAW_TEXT_KEYS)

    # Then
    assert result == {'tags': {'TITLE': 'xxxxxxx', 'ENCODER': 'xxxx'}}


def test_redact_does_not_break_track_lists() -> None:
    # Given a mediainfo document, whose `track` key holds the list of tracks
    data = {'media': {'@ref': '/movies/Some Movie.mkv', 'track': [{'@type': 'General', 'Format': 'Matroska'}]}}

    # When
    result = redact(data, RAW_TEXT_KEYS)

    # Then
    assert result['media']['track'] == [{'@type': 'General', 'Format': 'Matroska'}]
    assert result['media']['@ref'] == '/xxxxxx/xxxx xxxxx.xxx'


def test_redact_keeps_provider_information() -> None:
    # Given
    parsed = {'title': 'Some Movie', 'provider': {'name': 'ffmpeg', 'version': {'/usr/bin/ffprobe': 'v6.1.2'}}}

    # When
    result = redact(parsed, PARSED_TEXT_KEYS, PARSED_SKIP_KEYS)

    # Then
    assert result['title'] == 'xxxx xxxxx'
    assert result['provider'] == {'name': 'ffmpeg', 'version': {'/usr/bin/ffprobe': 'v6.1.2'}}


def test_redact_leaves_numbers_alone() -> None:
    # When
    result = redact({'title': 'x', 'width': 1920, 'frame_rate': 23.976}, PARSED_TEXT_KEYS)

    # Then
    assert result['width'] == 1920
    assert result['frame_rate'] == 23.976


def test_describe_path_names_every_non_ascii_character() -> None:
    # When
    info = describe_path('/movies/The Accountant² (2025)/movie ⅓.mkv')

    # Then
    assert info['non_ascii'] == [
        'U+00B2 SUPERSCRIPT TWO',
        'U+2153 VULGAR FRACTION ONE THIRD',
    ]


def test_describe_path_repr_is_pure_ascii() -> None:
    # Given a report must survive being pasted into any terminal or issue
    # When
    info = describe_path('/movies/café/⅓.mkv')

    # Then
    assert info['basename_repr'].isascii()


def test_describe_path_reports_normalization() -> None:
    # Given the same name composed and decomposed, as macOS and Linux store them
    composed = describe_path('/movies/café.mkv')
    decomposed = describe_path('/movies/café.mkv')

    # Then
    assert composed['is_nfc'] and not composed['is_nfd']
    assert decomposed['is_nfd'] and not decomposed['is_nfc']


def test_describe_path_hides_the_title_by_default() -> None:
    # When
    info = describe_path('/movies/Some Movie (2025).mkv')

    # Then
    assert 'Some' not in info['basename']
    assert info['basename'] == 'xxxx xxxxx (0000).xxx'


def test_describe_path_without_anonymize_keeps_the_name() -> None:
    # When
    info = describe_path('/movies/Some Movie (2025).mkv', anonymize=False)

    # Then
    assert info['basename'] == 'Some Movie (2025).mkv'


def test_describe_path_reports_a_missing_file() -> None:
    # When
    info = describe_path('/does/not/exist.mkv')

    # Then
    assert info['exists'] is False
    assert info['readable'] is False


def test_build_report_without_media_still_describes_the_environment() -> None:
    # When
    report = build_report()

    # Then
    assert report['knowit_bug_report'] == bugreport.REPORT_VERSION
    assert 'environment' in report
    assert 'media' not in report


def test_build_report_probes_every_provider(options: dict[str, typing.Any]) -> None:
    # Given
    video_path = 'tests/data/videos/test1.mkv'

    # When
    report = build_report([video_path], options)

    # Then
    media = report['media'][0]
    assert set(media['providers']) == {'mediainfo', 'ffmpeg', 'mkvmerge', 'enzyme'}
    for result in media['providers'].values():
        assert 'status' in result


def test_build_report_never_raises_on_a_missing_file(options: dict[str, typing.Any]) -> None:
    # When
    report = build_report(['/does/not/exist.mkv'], options)

    # Then
    assert report['media'][0]['path']['exists'] is False


def test_dump_report_is_valid_yaml(options: dict[str, typing.Any]) -> None:
    # Given
    report = build_report(['tests/data/videos/test1.mkv'], options)

    # When
    content = dump_report(report)

    # Then
    assert yaml.safe_load(content)['knowit_bug_report'] == bugreport.REPORT_VERSION


def test_dump_report_keeps_non_ascii_readable() -> None:
    # Given
    report = {'media': [{'path': describe_path('/movies/café.mkv', anonymize=False)}]}

    # When
    content = dump_report(report)

    # Then
    assert 'café.mkv' in content


def test_written_report_is_utf8(tmp_path: pathlib.Path, options: dict[str, typing.Any]) -> None:
    # Given
    destination = tmp_path / 'knowit-report.yml'
    content = dump_report(build_report(['tests/data/videos/test1.mkv'], options))

    # When
    destination.write_text(content, encoding='utf-8')

    # Then
    assert yaml.safe_load(destination.read_text(encoding='utf-8'))['knowit_version']
