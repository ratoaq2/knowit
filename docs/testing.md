# Testing

```bash
uv run pytest -q --tb=short tests
bash scripts/test.sh
```

## Recorded backend output

- The fixtures in `tests/conftest.py` monkeypatch the `Executor` of each provider. The executor then
  replays recorded JSON, XML, or YAML data and does not run a real binary. Thus most tests do not need
  mediainfo, ffmpeg, or mkvmerge.
- Each file in `tests/data/<provider>/` pairs the raw provider output with the expected parsed result.
  `assert_expected` in `tests/__init__.py` compares the structures.
- The repo holds no media files. `.gitignore` excludes `*.mkv`.
- To add a regression test from a user report, use `scripts/import_report.py`. See
  `docs/bug-reports.md`.

## Real media

The `*_real_media` tests download the Matroska test suite. They need the real tools. CI installs them with
`apt-get install mediainfo ffmpeg mkvtoolnix`.

## YAML cases

The rule and property unit tests (`tests/test_resolution.py`, `tests/test_audiochannels.py`,
`tests/test_properties.py`) get their cases from `parameters_from_yaml()` and the `tests/test_*.yml`
files. To add a case, add it to the YAML file. Do not write a new test function.
