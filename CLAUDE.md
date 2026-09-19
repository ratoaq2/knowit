# CLAUDE.md

Guidance for Claude Code when working in this repository.

## What this is

KnowIt is a small library + CLI that extracts structured metadata from video files
(codec, resolution, audio channels, subtitles, etc.) using one of four backends:
MediaInfo, FFmpeg (ffprobe), MKVToolNix (mkvmerge), or the pure-Python `enzyme` library
for MKV. Single flat package, no `src/` layout.

## Tooling

Package management, linting, formatting and type checking all go through **uv** and
**Ruff** — there is no separate venv activation step, always prefix commands with `uv run`.

```bash
uv sync                          # install/update the dev environment from uv.lock
uv run ruff check .              # lint
uv run ruff format .             # format
uv run mypy knowit tests         # strict type check (see below)
uv run pytest tests              # run the test suite
bash scripts/test.sh             # runs all four of the above, in order, like CI does
```

`uv run pre-commit run --all-files` runs the same ruff+mypy hooks pre-commit would run
on commit (`.pre-commit-config.yaml`).

**After editing code in this repo, run `ruff check --fix`, `ruff format`, `mypy`, and the
relevant tests before considering a change done** — don't just describe what should be run.

### mypy is strict — know the escape hatches

`[tool.mypy]` sets `strict = true`. The codebase is 100% clean under it; keep it that way.
A few patterns recur because of how this codebase's dynamic runtime data meets static types:

- **`Property[T]`'s `value` parameter is `typing.Any`, not `T`.** `T` describes what
  `handle()` *returns* (the parsed/typed result), not what it receives — the input is
  always raw, untyped track data from mediainfo/ffprobe/mkvmerge/enzyme. Don't "fix" this
  back to `T`; it was deliberately loosened in `knowit/core.py` to make every subclass's
  override honest (see `Configurable.handle`'s `typing.cast(str, value)` for how it
  reconciles the raw input with its own string-based key lookups).
- **`Configurable._extract_key` returns `str | typing.Literal[False]`**, not `str | bool`.
  `False` is a real sentinel meaning "skip the lookup, don't warn" — it is never `True`.
  Modeling it as `Literal[False]` lets mypy narrow the return to plain `str` after an
  `is False` check; `bool` would leave a phantom `Literal[True]` behind.
- **`Config` (in `knowit/config.py`) is a dynamic attribute bag.** `Config.build()`
  replaces `self.__dict__` wholesale with sections keyed by class name (`AudioCodec`,
  `VideoCodec`, `ScanType`, ...), populated from `defaults.yml`. It declares
  `__getattr__(self, item: str) -> typing.Any` purely so mypy allows arbitrary
  `config.AudioCodec`-style access — don't add real attributes expecting IDE completion.
- **mypy's analysis platform is pinned to `linux`** (`platform = "linux"` in
  `pyproject.toml`), matching CI (`ubuntu-latest`) and the Docker image. This project
  targets Linux; a contributor on Windows/macOS running `mypy` locally sees the same
  errors CI would. This matters for platform-conditional stdlib stubs (e.g.
  `ctypes.WinDLL`, used defensively in `mediainfo.py` and gated behind a
  `# type: ignore[attr-defined]` that is only "needed" on this pinned platform).

### Ruff config notes

- Single quotes (`quote-style = "single"` in `[tool.ruff.format]`) — matches the existing
  codebase convention, not Ruff's Black-compatible default.
- Rule set: `E, W, F, D, I, N, B, UP, C4, SIM` (pycodestyle, pyflakes, docstrings,
  isort, naming, bugbear, pyupgrade, comprehensions, simplify).
- `D100`/`D103` (missing module/function docstrings) are ignored project-wide.
  `**/__init__.py` additionally ignores `D104`/`F401` (re-export packages).

## Architecture

```
knowit/
  api.py           # public entry points: know(), dependencies(), initialize()
  __main__.py       # CLI (argparse) — thin wrapper around api.know()
  config.py         # loads defaults.yml (+ optional user config) into a Config object
  core.py           # base classes: Reportable, Property, Configurable, MultiValue, Rule
  provider.py       # Provider / Executor abstractions shared by all four backends
  serializer.py     # YAML/JSON dump helpers, custom YAML loader/dumper
  units.py          # pint UnitRegistry wrapper (falls back to NullRegistry if pint absent)
  utils.py          # path/candidate-finding helpers, OS detection
  properties/       # Property subclasses describing *what* a field is (codec, language, ...)
  providers/        # one module per backend: mediainfo.py, ffmpeg.py, mkvmerge.py, enzyme.py
  rules/            # Rule subclasses that post-process/derive fields (e.g. resolution, atmos)
  defaults.yml       # the actual codec/profile/etc. knowledge base, keyed by Property class name
```

**How a lookup flows**: `api.know(path, context)` picks the first `Provider` whose
`accepts()` returns True, calls `describe()`, which delegates to `Provider._describe_tracks()`
→ `_describe_track()` per track. Each track's fields come from the provider's `mapping`
(a dict of `Property`/`Configurable` instances keyed by output field name, `None` as a
placeholder for fields a `Rule` fills in instead) and then `rules` are applied on top.

- **`Property`**: extracts + transforms one field from raw track data (`Quantity` adds a
  unit, `Duration` parses timestamps, `Basic` coerces to a data type, ...).
- **`Configurable`**: a `Property` whose result comes from a `defaults.yml`-backed lookup
  table (codec names → canonical names, keyed off `Config.<ClassName>`). The lookup key
  comes from `_extract_key()`; `_extract_fallback_key()` lets a subclass retry with a
  looser key (e.g. `AudioCodec` strips everything after a `/`).
- **`Rule`**: runs after all `Property` extraction for a track, sees the already-built
  `props`/`pv_props` dicts, and can add/override/delete fields (e.g. `ResolutionRule`
  derives `1080p` from width/height/aspect ratio; `AtmosRule` rewrites the codec when
  Dolby Atmos is detected).
- **`Executor`**: wraps the actual external process/library call (e.g.
  `MediaInfoCliExecutor` shells out to the `mediainfo` binary, `MediaInfoCTypesExecutor`
  loads `libmediainfo` via ctypes). `NotFoundExecutor` is a null-object stand-in when
  nothing is installed — its `__bool__` is always `False`, which is how `Provider.loaded()`
  detects it.

Exceptions: `KnowitException` (raised by `api.know()` on any internal failure, wraps
`debug_info()` for bug reports) and `ProviderError`/`MalformedFileError`/
`UnsupportedFileFormatError` (raised by providers, caught by `know()`).

## Tests

- `tests/conftest.py` fixtures monkeypatch each provider's `Executor` to replay canned
  JSON/XML/YAML fixture data instead of shelling out to real binaries — most tests don't
  need mediainfo/ffmpeg/mkvmerge actually installed.
- `tests/data/<provider>/*.yml` (or `.xml`/`.json`) pair raw provider output with the
  expected parsed result; `tests/__init__.py::assert_expected` does the structural diff.
- A handful of `*_real_media` tests download the real Matroska test suite and need the
  actual external tools installed (this is what `apt-get install mediainfo ffmpeg
  mkvtoolnix` in CI is for).
- Rule/property unit tests (`test_resolution.py`, `test_audiochannels.py`,
  `test_properties.py`) are YAML-parametrized via `parameters_from_yaml()` against
  `tests/test_*.yml` fixture files, not hardcoded cases.
