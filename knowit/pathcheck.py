"""Reproduce path related problems without the media file that triggered them.

The most frequent reports are not about the content of a file, they are about its name:
a superscript, a fraction, an accent, or a character the file system encoding cannot
represent. Those need the name, not the media. This module writes a small sample under
that name and compares the result against the same sample under a plain ascii name.
"""

import os
import shutil
import tempfile
import traceback
import typing

from knowit import api
from knowit.bugreport import describe_path


def _element(element_id: bytes, payload: bytes) -> bytes:
    """Build an EBML element. Payloads are always shorter than 127 bytes here."""
    return element_id + bytes([0x80 | len(payload)]) + payload


def _build_minimal_mkv() -> bytes:
    """Build the smallest file every backend still recognises as Matroska."""
    header = _element(
        b'\x1a\x45\xdf\xa3',
        b''.join(
            (
                _element(b'\x42\x86', b'\x01'),  # EBMLVersion
                _element(b'\x42\xf7', b'\x01'),  # EBMLReadVersion
                _element(b'\x42\xf2', b'\x04'),  # EBMLMaxIDLength
                _element(b'\x42\xf3', b'\x08'),  # EBMLMaxSizeLength
                _element(b'\x42\x82', b'matroska'),  # DocType
                _element(b'\x42\x87', b'\x04'),  # DocTypeVersion
                _element(b'\x42\x85', b'\x02'),  # DocTypeReadVersion
            )
        ),
    )
    info = _element(
        b'\x15\x49\xa9\x66',
        b''.join(
            (
                _element(b'\x2a\xd7\xb1', b'\x0f\x42\x40'),  # TimestampScale
                _element(b'\x4d\x80', b'knowit'),  # MuxingApp
                _element(b'\x57\x41', b'knowit'),  # WritingApp
            )
        ),
    )
    return header + _element(b'\x18\x53\x80\x67', info)


#: A 75 byte Matroska file, used when the reporter has no file to share.
MINIMAL_MKV = _build_minimal_mkv()

#: The name the sample is given as a control, to tell a name problem from a file problem.
CONTROL_NAME = 'knowit-control.mkv'

#: Names that have appeared in reports, kept as a regression matrix.
ADVERSARIAL_NAMES = (
    'The Accountant² (2025).mkv',
    'Naked Gun 33⅓ - The Final Insult (1994).mkv',
    'Jellal vs Oración Seis.mkv',
    'Everyone’s Dignity.mkv',
    'What If… T’Challa Became a Star-Lord.mkv',
    'Umlaute äöüß.mkv',
    "KonoSuba – God's blessing.mkv",
    'café decomposed.mkv',
    'symbols [1080p] + extra.mkv',
    '日本語のタイトル.mkv',
    'Русский.mkv',
    'emoji \U0001f3ac.mkv',
)


def probe_name(
    directory: str,
    name: str,
    sample: bytes,
    context: typing.Mapping[str, typing.Any] | None = None,
) -> dict[str, typing.Any]:
    """Write the sample under `name` and report how each backend copes with it."""
    context = dict(context or {})
    context.setdefault('profile', 'code')

    result: dict[str, typing.Any] = {}
    video_path = os.path.join(directory, name)

    try:
        with open(video_path, 'wb') as stream:
            stream.write(sample)
    except (OSError, UnicodeError):
        result['created'] = False
        result['error'] = traceback.format_exc()
        return result

    result['created'] = True
    result['path'] = describe_path(video_path, anonymize=False)

    api.initialize(context)
    providers: dict[str, typing.Any] = {}
    for provider_name in api.provider_names:
        provider = api.available_providers.get(provider_name)
        if provider is None or not provider.loaded():
            providers[provider_name] = {'status': 'not installed'}
            continue
        if not provider.accepts(video_path):
            providers[provider_name] = {'status': 'does not accept this file'}
            continue

        try:
            provider.describe(video_path, dict(context))
            providers[provider_name] = {'status': 'ok'}
        except Exception as error:
            providers[provider_name] = {
                'status': 'error',
                'error': f'{type(error).__name__}: {error}',
                'traceback': traceback.format_exc(),
            }

    result['providers'] = providers
    return result


def check_name(
    name: str,
    context: typing.Mapping[str, typing.Any] | None = None,
    source: str | os.PathLike[str] | None = None,
) -> dict[str, typing.Any]:
    """Check whether a file name alone makes a backend fail.

    The same bytes are probed twice: once under a plain ascii name, once under `name`.
    A backend that only fails on the second one has a name handling problem. A backend
    that fails on both has a problem with the content, not with the name.
    """
    sample = MINIMAL_MKV
    if source is not None:
        with open(source, 'rb') as stream:
            sample = stream.read()

    directory = tempfile.mkdtemp(prefix='knowit-check-')
    try:
        control = probe_name(directory, CONTROL_NAME, sample, context)
        candidate = probe_name(directory, name, sample, context)
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    return {
        'name': name,
        'sample': 'the file you provided' if source is not None else 'a generated 75 byte Matroska file',
        'control': control,
        'candidate': candidate,
        'verdict': verdict(control, candidate),
    }


def verdict(control: typing.Mapping[str, typing.Any], candidate: typing.Mapping[str, typing.Any]) -> dict[str, str]:
    """Compare both probes and say, per backend, what the result means."""
    if not candidate.get('created'):
        return {'*': 'the file could not be created with this name'}

    result = {}
    control_providers = control.get('providers') or {}
    candidate_providers = candidate.get('providers') or {}
    for provider_name, candidate_result in candidate_providers.items():
        control_status = (control_providers.get(provider_name) or {}).get('status')
        candidate_status = candidate_result.get('status')

        if candidate_status == control_status:
            if candidate_status == 'error':
                result[provider_name] = 'fails with any name: not a name problem'
            else:
                result[provider_name] = f'{candidate_status}: the name is handled correctly'
        elif candidate_status == 'error':
            result[provider_name] = 'fails with this name only: the name is the problem'
        else:
            result[provider_name] = f'{control_status} -> {candidate_status}'

    return result
