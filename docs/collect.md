# Collect

`knowit --collect` captures the output of the providers for a whole media library. The maintainer uses
the capture to find wrong or missing values, to find raw fields that knowit does not read, and to make
test fixtures. The media is not needed.

## Flow

```bash
# What the user runs. Writes knowit-collect.jsonl.gz, and more parts for a large library.
knowit --collect /path/to/media
knowit --collect /path/to/media -o library.jsonl.gz -p ffmpeg --deep

# What the maintainer runs on the capture.
uv run python scripts/analyze_collect.py unknown library.jsonl.gz
uv run python scripts/analyze_collect.py disagree library.jsonl.gz
uv run python scripts/analyze_collect.py unmapped library.jsonl.gz
uv run python scripts/analyze_collect.py export library.jsonl.gz <key> --name <fixture-name>
```

## Format

`knowit/collect.py` owns the format. `COLLECT_VERSION` is its version. A reader stops on a newer version.

- JSON Lines. A `.gz` suffix gives gzip.
- Each part starts with a header line: the knowit version, `api.dependencies()`, the environment, and
  the options. A record belongs to the header above it.
- Each other line is the record of one file: `key`, `size`, `mtime`, `path` (from `describe_path()`),
  and `providers.<name>` with `status`, `seconds`, `raw`, `parsed`, and for ffmpeg with `--deep`, `deep`.
- `key` is the sha256 of the real path. The stored path is masked, so it cannot be the key.
- Redaction is the same as for `--bug-report` (see `docs/bug-reports.md`). Binary data (`BLOB_KEYS`) is
  removed, because masking keeps its length.

## What a capture tells about the media

Redaction masks the titles, the file names, the paths, the tags, and the home folder. It does not mask
the technical data, because the analysis needs it. Thus a capture can still help to identify a media
file:

- The exact file size, the duration, and the list of tracks can be the same for only one file.
- `key` is the sha256 of the real path. When a library uses a known naming scheme, a person can guess a
  path, calculate its key, and compare it.
- A masked name keeps its shape: the length of each word, the symbols, and the position of the digits.
  When there are only a few possible titles, the shape can show which one it is.
- The progress output in the terminal shows the real paths. The capture file does not contain them.

A capture made with `--no-redact` keeps all names.

## Parts and resume

- The writer flushes each line. A stop loses at most one line.
- Above `PART_SIZE`, the writer starts a new part: `name.part2.jsonl.gz`. Each part can be attached to a
  GitHub issue.
- A run never appends to an existing part. A gzip member that a crash cut would hide the lines after it.
  A new run starts a new part.
- At start, a run reads the keys of all parts. It skips a file with the same key, size, and mtime. The
  reader skips a damaged line or a cut gzip end.

## Deep probe

`--deep` runs a second ffprobe command on the first `DEEP_FRAMES` video frames and keeps
`DEEP_FRAME_KEYS` of each frame. The frame side data holds HDR10+ and the Dolby Vision RPU. The DOVI
configuration record is in the stream `side_data_list`, so the normal capture has it. The normal ffprobe
call does not change.

## Analysis

`scripts/analyze_collect.py` sends the raw output through the current code again (`describe_raw()` in
`scripts/import_report.py`). A new mapping or rule thus shows its effect on an old capture.

- `unknown`: the values that knowit does not know, with counts and an example key.
- `disagree`: the `FOCUS_FIELDS` where the providers give different values for the same track. The raw
  output has masked track names, so the replay cannot guess from them. The `NAME_FIELDS` thus come from
  the `parsed` output that the scan stored, with the code of the scan.
- `unmapped`: the raw fields that no provider mapping reads. The fields that match `KEYWORDS` come first
  (marked `*`), then the most frequent ones.
- `export`: writes the fixtures of one file to `tests/data/<provider>/`, as `import_report.py` does.
  An exported fixture still identifies the file (see above). Before you commit it, remove the tracks
  and the fields that the test does not need. Replace the durations, sizes, bit rates, and names with
  round values. Then write the `.yml` again from the replay.
