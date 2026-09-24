import pathlib
import typing

import pytest
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
from knowit.provider import ProviderError
from knowit.providers.ffmpeg import FFmpegProvider


def test_mask_text_hides_words_but_keeps_shape() -> None:
    # When
    masked = mask_text('The Accountant 2 (2025).mkv')

    # Then
    assert masked == 'xxx xxxxxxxxxx 0 (0000).xxx'


def test_mask_text_masks_non_ascii_letters_and_digits() -> None:
    # Given a title in any script identifies the media as much as an ascii title
    # When
    masked = mask_text('The Accountant² 33⅓ é – ８番出口 Україна')

    # Then symbols stay readable
    assert masked == 'xxx xxxxxxxxxx0 000 x – 0xxx xxxxxxx'


def test_redact_masks_known_free_text_keys() -> None:
    # Given
    data = {'Title': 'Some Episode Name', 'Format': 'Matroska', 'Width': '1920'}

    # When
    result = redact(data, RAW_TEXT_KEYS)

    # Then
    assert result == {'Title': 'xxxx xxxxxxx xxxx', 'Format': 'Matroska', 'Width': '1920'}


def test_redact_masks_encoded_library_version() -> None:
    # Given a custom encoder build, where the version holds the name of a release group
    data = {
        'Encoded_Library': 'x265 - 3.3+4-group:[Linux] 10bit',
        'Encoded_Library_String': 'x265 3.3+4-group:[Linux] 10bit',
        'Encoded_Library_Name': 'x265',
        'Encoded_Library_Version': '3.3+4-group:[Linux] 10bit',
    }

    # When
    result = redact(data, RAW_TEXT_KEYS)

    # Then the name stays readable, because knowit reads it
    assert result == {
        'Encoded_Library': 'x000 - 0.0+0-xxxxx:[xxxxx] 00xxx',
        'Encoded_Library_String': 'x000 0.0+0-xxxxx:[xxxxx] 00xxx',
        'Encoded_Library_Name': 'x265',
        'Encoded_Library_Version': '0.0+0-xxxxx:[xxxxx] 00xxx',
    }


def test_redact_masks_unique_ids_and_dates() -> None:
    # Given mkvmerge and mediainfo values that identify one file
    data = {
        'container': {
            'properties': {
                'segment_uid': 'ab12cd34ef56ab78',
                'date_utc': '2001-02-03T04:05:06Z',
                'date_local': '2001-02-03T04:05:06+00:00',
            },
        },
        'tracks': [{'properties': {'uid': 1234567890123456789, 'number': 1}}],
        'Encoded_Date': '2001-02-03 04:05:06 UTC',
        'Tagged_Date': '2001-02-03 04:05:06 UTC',
        'File_Modified_Date': '2002-03-04 05:06:07 UTC',
        'File_Modified_Date_Local': '2002-03-04 05:06:07',
    }

    # When
    result = redact(data, RAW_TEXT_KEYS)

    # Then
    assert result == {
        'container': {
            'properties': {
                'segment_uid': 'xx00xx00xx00xx00',
                'date_utc': '0000-00-00x00:00:00x',
                'date_local': '0000-00-00x00:00:00+00:00',
            },
        },
        'tracks': [{'properties': {'uid': 0, 'number': 1}}],
        'Encoded_Date': '0000-00-00 00:00:00 xxx',
        'Tagged_Date': '0000-00-00 00:00:00 xxx',
        'File_Modified_Date': '0000-00-00 00:00:00 xxx',
        'File_Modified_Date_Local': '0000-00-00 00:00:00',
    }


def test_redact_is_case_insensitive() -> None:
    # When
    result = redact({'tags': {'TITLE': 'Episode', 'ENCODER': 'Lavf'}}, RAW_TEXT_KEYS)

    # Then
    assert result == {'tags': {'TITLE': 'xxxxxxx', 'ENCODER': 'xxxx'}}


def test_redact_keeps_technical_tags() -> None:
    # Given ffprobe tags, where the track language and the statistics sit next to the title
    tags = {
        'language': 'eng',
        'title': 'Director Commentary',
        'BPS': '640000',
        'BPS-eng': '640000',
        'DURATION': '01:00:00.000000000',
        'NUMBER_OF_FRAMES': '112500',
        'NUMBER_OF_BYTES': '288000000',
        'mimetype': 'application/x-truetype-font',
    }

    # When
    result = redact({'streams': [{'tags': tags}]}, RAW_TEXT_KEYS)

    # Then
    assert result == {'streams': [{'tags': {**tags, 'title': 'xxxxxxxx xxxxxxxxxx'}}]}


def test_redact_masks_enzyme_track_and_chapter_names() -> None:
    # Given enzyme output, where track and chapter names can hold the movie title
    data = {
        'video_tracks': [{'name': 'Some Movie', 'codec_id': 'V_MPEGH/ISO/HEVC'}],
        'chapters': [{'string': 'The Heist', 'language': 'eng'}],
    }

    # When
    result = redact(data, RAW_TEXT_KEYS)

    # Then
    assert result == {
        'video_tracks': [{'name': 'xxxx xxxxx', 'codec_id': 'V_MPEGH/ISO/HEVC'}],
        'chapters': [{'string': 'xxx xxxxx', 'language': 'eng'}],
    }


def test_redact_masks_the_last_file_of_a_playlist() -> None:
    # Given a mediainfo track of a Blu-ray playlist, which names the folder of its last file
    track = {
        'FolderName_Last': '/storage/Some Movie/BDMV/STREAM',
        'FileName_Last': '00167',
        'FileNameExtension_Last': '00167.m2ts',
        'FileExtension_Last': 'm2ts',
    }

    # When
    result = redact(track, RAW_TEXT_KEYS)

    # Then
    assert result == {
        'FolderName_Last': '/xxxxxxx/xxxx xxxxx/xxxx/xxxxxx',
        'FileName_Last': '00000',
        'FileNameExtension_Last': '00000.x0xx',
        'FileExtension_Last': 'm2ts',
    }


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


def test_describe_path_hides_non_ascii_letters_and_digits_by_default() -> None:
    # When
    info = describe_path('/movies/８番出口 – café.mkv')

    # Then the path does not show the title, but shows that it has non-ascii characters
    assert info['basename'] == '0xxx – xxxx.xxx'
    assert info['non_ascii'] == ['U+2013 EN DASH', 'non-ascii letter', 'non-ascii number']


def test_describe_path_names_every_non_ascii_character() -> None:
    # When
    info = describe_path('/movies/The Accountant² (2025)/movie ⅓.mkv', anonymize=False)

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


def test_build_report_masks_the_path_in_a_provider_error(
    tmp_path: pathlib.Path, options: dict[str, typing.Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    # Given ffprobe quotes the path in its error message
    video = tmp_path / 'Some Movie (2024).mkv'
    video.write_bytes(b'\0' * 10)

    def failing_describe(self: FFmpegProvider, video_path: str, context: typing.Any) -> typing.Any:
        raise ProviderError(f'ffprobe failed with exit status 1: {video_path}: Invalid data found')

    monkeypatch.setattr(FFmpegProvider, 'describe', failing_describe)

    # When
    report = build_report([str(video)], options)

    # Then
    result = report['media'][0]['providers']['ffmpeg']
    assert 'Invalid data found' in result['traceback']
    assert 'Some Movie' not in result['traceback']
    assert str(tmp_path) not in result['traceback']
