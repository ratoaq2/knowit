"""Analyze the output of `knowit --collect`.

The capture holds the raw output of each provider. This script sends it through the
current code again, so a new mapping or rule shows its effect on an old capture without
a new scan of the library.

Usage:

    uv run python scripts/analyze_collect.py unknown library.jsonl.gz
    uv run python scripts/analyze_collect.py disagree library.jsonl.gz
    uv run python scripts/analyze_collect.py unmapped library.jsonl.gz
    uv run python scripts/analyze_collect.py export library.jsonl.gz <key> --name hdr10plus-example
"""

import argparse
import collections
import os
import sys
import typing

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import import_report  # noqa: E402

from knowit import api  # noqa: E402
from knowit.collect import COLLECT_VERSION, read_lines  # noqa: E402

#: Parsed fields that media players use. Only these are compared between providers.
FOCUS_FIELDS = (
    'codec',
    'profile',
    'hdr_format',
    'bit_depth',
    'channels',
    'channels_count',
    'language',
    'forced',
    'default',
    'hearing_impaired',
    'closed_caption',
    'commentary',
    'format',
)

#: Focus fields that knowit can guess from the track name. The replay sees masked names, so these come
#: from the parse that the scan stored.
NAME_FIELDS = ('language', 'hearing_impaired', 'closed_caption')

#: Raw field names with these words come first in the unmapped list.
KEYWORDS = (
    'hdr',
    'dolby',
    'dovi',
    'dv_',
    'atmos',
    'joc',
    'dts',
    'imax',
    'commentary',
    'sdh',
    'hearing',
    'visual',
    'descriptive',
    'forced',
    'original',
    'caption',
    'cc',
    'color',
    'colour',
    'mastering',
    'light_level',
    'side_data',
)

#: Values that each unmapped field shows as examples.
EXAMPLE_VALUES = 5

Counts = collections.Counter[typing.Any]


def load_records(output: str) -> dict[str, dict[str, typing.Any]]:
    """Return the last record of each file, by key."""
    records = {}
    for line in read_lines(output):
        if line.get('knowit_collect', COLLECT_VERSION) > COLLECT_VERSION:
            raise SystemExit(f'{output} has format {line["knowit_collect"]}. Update knowit to read it.')
        if 'key' in line:
            records[line['key']] = line
    return records


def raw_outputs(record: typing.Mapping[str, typing.Any]) -> typing.Iterator[tuple[str, typing.Any]]:
    """Yield the provider name and the raw output of each provider that gave one."""
    for name, result in (record.get('providers') or {}).items():
        if result.get('raw'):
            yield name, result['raw']


def replay(
    name: str, record: typing.Mapping[str, typing.Any], raw: typing.Any, report: dict[str, typing.Any] | None = None
) -> typing.Any:
    """Describe the raw output with the current code. Return None when it fails."""
    context: dict[str, typing.Any] = {'profile': 'code', 'path': record['key']}
    if report is not None:
        context['report'] = report
    try:
        return import_report.describe_raw(name, f'{record["key"]}.mkv', raw, context)
    except Exception:
        return None


def find_unknown(records: typing.Mapping[str, typing.Mapping[str, typing.Any]]) -> tuple[Counts, dict[typing.Any, str]]:
    """Count the unknown values of each provider, with one example key."""
    counts: Counts = collections.Counter()
    examples: dict[typing.Any, str] = {}
    for key, record in records.items():
        for name, raw in raw_outputs(record):
            report: dict[str, typing.Any] = {}
            replay(name, record, raw, report)
            for description, values in report.items():
                for value in values:
                    item = (name, description, value)
                    counts[item] += 1
                    examples.setdefault(item, key)
    return counts, examples


def _text(value: typing.Any) -> str | None:
    """Return a comparable text for a parsed value."""
    return None if value is None else str(value)


def find_disagreements(
    records: typing.Mapping[str, typing.Mapping[str, typing.Any]],
) -> tuple[Counts, dict[typing.Any, str]]:
    """Count the focus fields where the providers give different values for the same track."""
    counts: Counts = collections.Counter()
    examples: dict[typing.Any, str] = {}
    for key, record in records.items():
        parsed = {name: replay(name, record, raw) or {} for name, raw in raw_outputs(record)}
        if len(parsed) < 2:
            continue
        names = sorted(parsed)
        stored = {name: record['providers'][name].get('parsed') or parsed[name] for name in names}
        for track_type in ('video', 'audio', 'subtitle'):
            replayed = {name: parsed[name].get(track_type) or [] for name in names}
            guessed = {name: stored[name].get(track_type) or [] for name in names}
            for index in range(max(len(t) for t in (*replayed.values(), *guessed.values()))):
                for field in FOCUS_FIELDS:
                    tracks = guessed if field in NAME_FIELDS else replayed
                    values = tuple(
                        (name, _text(tracks[name][index].get(field)) if index < len(tracks[name]) else None)
                        for name in names
                    )
                    if len({value for _, value in values}) > 1:
                        item = (f'{track_type}.{field}', values)
                        counts[item] += 1
                        examples.setdefault(item, key)
    return counts, examples


def mapped_names(name: str) -> set[str]:
    """Return the raw field names that the mapping of a provider reads, in lower case."""
    provider = api.available_providers.get(name)
    if provider is None:
        return set()
    return {
        field.lower()
        for track in provider.mapping.values()
        for prop in track.values()
        if prop is not None
        for field in getattr(prop, 'names', ())
    }


def flatten(data: typing.Any, prefix: str = '') -> typing.Iterator[tuple[str, typing.Any]]:
    """Yield the dotted path and the value of each leaf. A list adds `[]` to the path."""
    if isinstance(data, dict):
        for key, value in data.items():
            yield from flatten(value, f'{prefix}.{key}' if prefix else str(key))
    elif isinstance(data, list):
        for item in data:
            yield from flatten(item, f'{prefix}[]')
    else:
        yield prefix, data


def is_mapped(path: str, names: typing.AbstractSet[str]) -> bool:
    """Return True when a mapping name is the end of the path."""
    lowered = path.lower().replace('[]', '')
    return any(lowered == name or lowered.endswith(f'.{name}') for name in names)


def find_unmapped(
    records: typing.Mapping[str, typing.Mapping[str, typing.Any]],
) -> tuple[Counts, dict[typing.Any, Counts]]:
    """Count the files that have each raw field that no mapping reads, with example values."""
    files: Counts = collections.Counter()
    values: dict[typing.Any, Counts] = collections.defaultdict(collections.Counter)
    names = {name: mapped_names(name) for name in api.provider_names}
    for record in records.values():
        for name, raw in raw_outputs(record):
            seen = set()
            for path, value in flatten(raw):
                if is_mapped(path, names[name]):
                    continue
                item = (name, path)
                seen.add(item)
                values[item][str(value)[:60]] += 1
            files.update(seen)
    return files, values


def rank(path: str) -> int:
    """Return 0 for a path with a keyword, else 1."""
    lowered = path.lower()
    return 0 if any(word in lowered for word in KEYWORDS) else 1


def command_unknown(records: typing.Mapping[str, typing.Any], top: int) -> None:
    """Print the unknown values."""
    counts, examples = find_unknown(records)
    for (name, description, value), count in counts.most_common(top):
        print(f'{count:6d}  {name:9s}  {description}: {value!r}  e.g. {examples[(name, description, value)]}')


def command_disagree(records: typing.Mapping[str, typing.Any], top: int) -> None:
    """Print the provider disagreements."""
    counts, examples = find_disagreements(records)
    for (field, values), count in counts.most_common(top):
        shown = ', '.join(f'{name}={value}' for name, value in values)
        print(f'{count:6d}  {field}: {shown}  e.g. {examples[(field, values)]}')


def command_unmapped(records: typing.Mapping[str, typing.Any], top: int) -> None:
    """Print the unmapped raw fields: fields with a keyword first, then the most frequent."""
    files, values = find_unmapped(records)
    items = sorted(files, key=lambda item: (rank(item[1]), -files[item], item))
    for item in items[:top]:
        name, path = item
        examples = ', '.join(f'{value!r} ({n})' for value, n in values[item].most_common(EXAMPLE_VALUES))
        marker = '*' if rank(path) == 0 else ' '
        print(f'{files[item]:6d} {marker} {name:9s}  {path}: {examples}')


def command_export(
    records: typing.Mapping[str, typing.Any], key: str, name: str, data_root: str, overwrite: bool
) -> int:
    """Write the fixtures of one file."""
    matches = [record for record_key, record in records.items() if record_key.startswith(key)]
    if len(matches) != 1:
        print(f'{len(matches)} files match the key {key!r}. Give a longer key.', file=sys.stderr)
        return 1
    written = import_report.import_report({'media': matches}, name, overwrite=overwrite, data_root=data_root)
    for path in written:
        print(f'wrote {path}')
    return 0 if written else 1


def build_argument_parser() -> argparse.ArgumentParser:
    """Build the argument parser."""
    opts = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = opts.add_subparsers(dest='command', required=True)
    for command in ('unknown', 'disagree', 'unmapped'):
        sub = commands.add_parser(command)
        sub.add_argument('output', help='The collect output, for example library.jsonl.gz')
        sub.add_argument('--top', type=int, default=50, help='Number of lines to show, default 50')
    export = commands.add_parser('export')
    export.add_argument('output', help='The collect output, for example library.jsonl.gz')
    export.add_argument('key', help='The key of the file, or the start of it')
    export.add_argument('--name', required=True, help='Fixture base name')
    export.add_argument('--data-root', default=import_report.DATA_ROOT, help='Where the fixtures are written')
    export.add_argument('--overwrite', action='store_true', help='Replace fixtures that already exist')
    return opts


def main(args: list[str] | None = None) -> int:
    """Execute the main function for the entry point."""
    options = build_argument_parser().parse_args(args)
    records = load_records(options.output)
    print(f'{len(records)} files in {options.output}', file=sys.stderr)
    api.initialize({})

    if options.command == 'export':
        return command_export(records, options.key, options.name, options.data_root, options.overwrite)

    commands = {'unknown': command_unknown, 'disagree': command_disagree, 'unmapped': command_unmapped}
    commands[options.command](records, options.top)
    return 0


if __name__ == '__main__':
    sys.exit(main())
