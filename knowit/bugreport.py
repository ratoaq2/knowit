"""Build a self-contained bug report that can be attached to an issue.

Reproducing a knowit bug almost never needs the media file itself: it needs the raw
output the backend produced for it. That output is a few kilobytes of text, it carries
no copyrighted content, and it is exactly what `tests/data/<provider>` is made of.
"""

import datetime
import json
import os
import sys
import traceback
import typing
import unicodedata

import yaml

from knowit import __version__, api
from knowit.environment import collect_environment
from knowit.serializer import get_yaml_dumper

#: Bumped whenever the report layout changes in a way readers must know about.
REPORT_VERSION = 1

#: Free text in raw backend output. Values are masked, never dropped.
RAW_TEXT_KEYS = frozenset(
    {
        '@ref',
        'album',
        'album_performer',
        'artist',
        'author',
        'comment',
        'comment_ext',
        'completename',
        'completename_last',
        'composer',
        'contenttype',
        'copyright',
        'cover_data',
        'description',
        'director',
        'encoded_by',
        'episode_id',
        'file_name',
        'filename',
        'filenameextension',
        'folder',
        'foldername',
        'isrc',
        'keywords',
        'label',
        'lyrics',
        'movie',
        'movie_more',
        'part',
        'performer',
        'producer',
        'segment_filename',
        'show',
        'summary',
        'synopsis',
        'title',
        'track_more',
        'track_name',
        'uniqueid',
        'uniqueid_string',
        'writtenby',
    }
)

#: Free text in knowit's own parsed output.
PARSED_TEXT_KEYS = frozenset({'name', 'path', 'title'})

#: Subtrees that describe knowit itself and must survive redaction intact.
PARSED_SKIP_KEYS = frozenset({'provider'})

#: Subtrees whose every string value is free text, whatever the key is called.
OPAQUE_SUBTREE_KEYS = frozenset({'extra', 'tags'})


def mask_text(value: str) -> str:
    """Mask free text while keeping its shape.

    Ascii letters and digits are replaced, so the wording is gone. Everything else is
    kept verbatim: separators, and above all non-ascii characters, which are the whole
    subject of most path-related reports and are not themselves the private part.
    """
    masked = []
    for char in value:
        if not char.isascii():
            masked.append(char)
        elif char.isdigit():
            masked.append('0')
        elif char.isalpha():
            masked.append('x')
        else:
            masked.append(char)
    return ''.join(masked)


def redact(
    data: typing.Any,
    keys: typing.AbstractSet[str],
    skip_keys: typing.AbstractSet[str] = frozenset(),
    mask_everything: bool = False,
) -> typing.Any:
    """Return a copy of `data` with free text masked."""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            lowered = str(key).lower()
            if lowered in skip_keys:
                result[key] = value
            elif lowered in OPAQUE_SUBTREE_KEYS:
                result[key] = redact(value, keys, skip_keys, mask_everything=True)
            else:
                result[key] = redact(value, keys, skip_keys, mask_everything or lowered in keys)
        return result

    if isinstance(data, list):
        return [redact(item, keys, skip_keys, mask_everything) for item in data]

    if mask_everything and isinstance(data, str):
        return mask_text(data)

    return data


def describe_path(path: str | os.PathLike[str], anonymize: bool = True) -> dict[str, typing.Any]:
    """Describe a path in a way that is safe to publish but keeps the failing detail.

    For the most common class of report -- "knowit cannot open this file" -- the path is
    the bug. This keeps the exact characters that trigger it, plus the encoding facts
    needed to reproduce it, without disclosing the title.
    """
    text = os.fspath(path)
    directory, basename = os.path.split(text)
    mask = mask_text if anonymize else str

    non_ascii = {char for char in text if not char.isascii()}
    filesystem_encoding = sys.getfilesystemencoding()
    try:
        text.encode(filesystem_encoding)
        encodable = True
    except UnicodeError:
        encodable = False

    info: dict[str, typing.Any] = {
        'directory': mask(directory),
        'basename': mask(basename),
        'basename_repr': ascii(mask(basename)),
        'length': len(text),
        'non_ascii': sorted(_describe_char(char) for char in non_ascii),
        'is_nfc': unicodedata.is_normalized('NFC', text),
        'is_nfd': unicodedata.is_normalized('NFD', text),
        'has_surrogates': any(0xD800 <= ord(char) <= 0xDFFF for char in text),
        'filesystem_encoding': filesystem_encoding,
        'encodable_to_filesystem_encoding': encodable,
    }

    try:
        info['exists'] = os.path.exists(text)
        info['is_file'] = os.path.isfile(text)
        info['readable'] = os.access(text, os.R_OK)
        if info['is_file']:
            info['size'] = os.path.getsize(text)
    except OSError as error:
        info['stat_error'] = f'{type(error).__name__}: {error}'

    return info


def _describe_char(char: str) -> str:
    """Return a printable identity for a character, usable in a public issue."""
    name = unicodedata.name(char, '<unnamed>')
    return f'U+{ord(char):04X} {name}'


def _raw_data(context: typing.Mapping[str, typing.Any]) -> typing.Any:
    """Return the backend's raw output as structured data."""
    debug_data = context.get('debug_data')
    if not callable(debug_data):
        return None
    try:
        dumped = debug_data()
    except Exception:
        return {'error': traceback.format_exc()}
    try:
        return json.loads(dumped)
    except ValueError:
        return dumped


def probe_provider(
    name: str,
    video_path: str,
    context: typing.Mapping[str, typing.Any],
    anonymize: bool = True,
) -> dict[str, typing.Any]:
    """Run a single backend and capture whatever it produced, failure included."""
    result: dict[str, typing.Any] = {}
    provider = api.available_providers.get(name)
    if provider is None:
        return {'status': 'unavailable'}

    result['location'] = getattr(provider.executor, 'location', None) or name
    if not provider.loaded():
        result['status'] = 'not installed'
        return result
    if not provider.accepts(video_path):
        result['status'] = 'does not accept this file'
        return result

    probe_context: dict[str, typing.Any] = {**context, 'profile': 'code'}
    parsed = None
    try:
        parsed = provider.describe(video_path, probe_context)
        result['status'] = 'ok'
    except Exception:
        result['status'] = 'error'
        result['traceback'] = traceback.format_exc()

    raw = _raw_data(probe_context)
    if raw is not None:
        result['raw'] = redact(raw, RAW_TEXT_KEYS) if anonymize else raw
    if parsed:
        result['parsed'] = redact(parsed, PARSED_TEXT_KEYS, PARSED_SKIP_KEYS) if anonymize else parsed

    return result


def build_media_report(
    video_path: str | os.PathLike[str],
    context: typing.Mapping[str, typing.Any] | None = None,
    anonymize: bool = True,
) -> dict[str, typing.Any]:
    """Build the per-file part of a report, probing every installed backend."""
    context = dict(context or {})
    context.setdefault('profile', 'code')
    text = os.fspath(video_path)

    report: dict[str, typing.Any] = {'path': describe_path(text, anonymize)}
    try:
        api.initialize(context)
    except Exception:
        report['initialization_error'] = traceback.format_exc()
        return report

    providers = {}
    for name in api.provider_names:
        try:
            providers[name] = probe_provider(name, text, context, anonymize)
        except Exception:
            providers[name] = {'status': 'error', 'traceback': traceback.format_exc()}
    report['providers'] = providers

    return report


def build_report(
    video_paths: typing.Iterable[str | os.PathLike[str]] = (),
    context: typing.Mapping[str, typing.Any] | None = None,
    anonymize: bool = True,
) -> dict[str, typing.Any]:
    """Build a complete bug report. This never raises: a partial report still helps."""
    context = dict(context or {})
    report: dict[str, typing.Any] = {
        'knowit_bug_report': REPORT_VERSION,
        'generated_at': datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        'knowit_version': __version__,
        'anonymized': anonymize,
    }

    try:
        report['environment'] = collect_environment(context)
    except Exception:
        report['environment'] = {'error': traceback.format_exc()}

    media = []
    for video_path in video_paths:
        try:
            media.append(build_media_report(video_path, context, anonymize))
        except Exception:
            media.append({'error': traceback.format_exc()})
    if media:
        report['media'] = media

    return report


def dump_report(report: typing.Mapping[str, typing.Any]) -> str:
    """Render a report as YAML, using the same value formatting as the fixtures."""
    return yaml.dump(
        dict(report),
        Dumper=get_yaml_dumper({'profile': 'code'}),
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=120,
    )


def default_output_path() -> str:
    """Return the file a report is written to when no destination is given.

    The name never repeats the media name: the report masks titles, so putting one in
    the file name the user uploads would defeat that.
    """
    return 'knowit-report.yml'
