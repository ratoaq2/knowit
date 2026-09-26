"""Turn a user bug report into test fixtures.

A report produced by `knowit --bug-report` holds the raw output of every backend for the
file that failed. That output is what `tests/data/<provider>` is made of, so a report can
become a regression test without the reporter ever sending their media.

Usage:

    uv run python scripts/import_report.py knowit-report.yml --issue 220
    uv run pytest tests -k issue-220
"""

import argparse
import json
import os
import sys
import typing

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowit import api  # noqa: E402
from knowit.providers import EnzymeProvider  # noqa: E402

DATA_ROOT = os.path.join('tests', 'data')


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    opts = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    opts.add_argument(dest='report', help='The knowit-report.yml file sent by the reporter', type=str)
    opts.add_argument('--issue', dest='issue', help='The issue number, used to name the fixtures', type=str)
    opts.add_argument('--name', dest='name', help='Fixture base name, instead of issue-<number>-example', type=str)
    opts.add_argument(
        '--no-replay',
        action='store_true',
        dest='no_replay',
        help='Write the expected values from the report instead of replaying the raw data',
    )
    opts.add_argument(
        '--data-root',
        dest='data_root',
        default=DATA_ROOT,
        help=f'Where the fixtures are written, default {DATA_ROOT}',
        type=str,
    )
    opts.add_argument(
        '--overwrite',
        action='store_true',
        dest='overwrite',
        help='Replace fixtures that already exist',
    )
    return opts


def replay(provider_name: str, video_path: str, raw: typing.Any) -> typing.Any:
    """Run the current code over the raw data, the way the test suite does.

    This keeps the fixture self consistent: some providers read the path from the raw
    data and some from the file name, and a hand written expectation gets that wrong.
    """
    api.available_providers.clear()
    api.initialize({})
    return describe_raw(provider_name, video_path, raw)


def describe_raw(
    provider_name: str,
    video_path: str,
    raw: typing.Any,
    context: dict[str, typing.Any] | None = None,
) -> typing.Any:
    """Run the current code over the raw data, with the providers that are already initialized."""
    provider = api.available_providers.get(provider_name)
    if provider is None:
        return None

    context = context if context is not None else {'profile': 'code'}
    if provider_name == 'enzyme':
        original_classmethod = EnzymeProvider.extract_info
        EnzymeProvider.extract_info = classmethod(lambda cls, filename: raw)  # type: ignore[assignment,method-assign]
        try:
            return provider.describe(video_path, context)
        finally:
            EnzymeProvider.extract_info = original_classmethod  # type: ignore[method-assign]

    executor = provider.executor
    if executor is None or not provider.loaded():
        return None

    original = executor.extract_info
    executor.extract_info = lambda filename: raw  # type: ignore[method-assign]
    try:
        return provider.describe(video_path, context)
    finally:
        executor.extract_info = original  # type: ignore[method-assign]


def write_fixture(
    provider_name: str,
    base_name: str,
    raw: typing.Any,
    expected: typing.Any,
    overwrite: bool,
    data_root: str = DATA_ROOT,
) -> list[str]:
    """Write the raw and the expected files for one provider."""
    directory = os.path.join(data_root, provider_name)
    os.makedirs(directory, exist_ok=True)

    written = []
    json_path = os.path.join(directory, f'{base_name}.json')
    yaml_path = os.path.join(directory, f'{base_name}.yml')

    for path in (json_path, yaml_path):
        if os.path.exists(path) and not overwrite:
            print(f'  {path} already exists, use --overwrite')
            return []

    with open(json_path, 'w', encoding='utf-8') as stream:
        # Escaped ascii, so the fixture reads back the same whatever locale the reader has.
        json.dump(raw, stream, indent=4, ensure_ascii=True)
        stream.write('\n')
    written.append(json_path)

    if expected:
        with open(yaml_path, 'w', encoding='utf-8') as stream:
            yaml.safe_dump(expected, stream, default_flow_style=False, allow_unicode=True, sort_keys=False)
        written.append(yaml_path)
    else:
        print(f'  no expected values for {provider_name}, write {yaml_path} by hand')

    return written


def import_report(
    report: typing.Mapping[str, typing.Any],
    base_name: str,
    replay_raw: bool = True,
    overwrite: bool = False,
    data_root: str = DATA_ROOT,
) -> list[str]:
    """Write one fixture pair per provider that produced raw output."""
    written = []
    for index, media in enumerate(report.get('media') or [], start=1):
        suffix = f'-{index:02d}' if len(report.get('media') or []) > 1 else ''
        name = f'{base_name}{suffix}.mkv'

        for provider_name, result in (media.get('providers') or {}).items():
            raw = result.get('raw')
            if not raw:
                continue

            print(f'{provider_name}: status {result.get("status")}')
            video_path = os.path.join(data_root, provider_name, name)
            expected = result.get('parsed')
            if replay_raw:
                replayed = None
                try:
                    replayed = replay(provider_name, video_path, raw)
                except Exception as error:
                    print(f'  replay failed: {type(error).__name__}: {error}')
                if replayed:
                    expected = yaml.safe_load(
                        yaml.dump(replayed, Dumper=_dumper(), allow_unicode=True, sort_keys=False)
                    )

            written.extend(write_fixture(provider_name, name, raw, _strip_version(expected), overwrite, data_root))

    return written


def _strip_version(expected: typing.Any) -> typing.Any:
    """Drop the provider version, which the test suite ignores and which changes often."""
    if isinstance(expected, dict) and isinstance(expected.get('provider'), dict):
        expected['provider'] = {k: v for k, v in expected['provider'].items() if k != 'version'}
    return expected


def _dumper() -> type[yaml.SafeDumper]:
    """Return the dumper knowit uses for its own output."""
    from knowit.serializer import get_yaml_dumper

    return get_yaml_dumper({'profile': 'code'})


def main(args: list[str] | None = None) -> int:
    """Execute the main function for the entry point."""
    options = build_argument_parser().parse_args(args)

    with open(options.report, encoding='utf-8') as stream:
        report = yaml.safe_load(stream)

    if not isinstance(report, dict) or 'knowit_bug_report' not in report:
        print(f'{options.report} is not a knowit bug report', file=sys.stderr)
        return 1

    base_name = options.name or (f'issue-{options.issue}-example' if options.issue else 'imported-example')

    environment = report.get('environment') or {}
    knowit_section = environment.get('knowit') or {}
    print(f'Report from knowit {report.get("knowit_version")} ({knowit_section.get("installation", "unknown")})')
    if report.get('anonymized'):
        print('Titles and file names in this report are masked.')
    print()

    written = import_report(
        report,
        base_name,
        replay_raw=not options.no_replay,
        overwrite=options.overwrite,
        data_root=options.data_root,
    )

    print()
    if not written:
        print('No fixture was written.')
        return 1

    for path in written:
        print(f'wrote {path}')
    print()
    print('Next steps:')
    print(f'  uv run pytest tests -k {base_name}')
    print('  Correct the .yml files to the values you expect, then fix the code.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
