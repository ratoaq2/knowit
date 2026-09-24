# Architecture

knowit is a library and a CLI. It reads a video file with one of four backends and returns structured
metadata. The package is flat: `knowit/`.

## Modules

| Module | Role |
| --- | --- |
| `knowit/api.py` | Public entry points: `know()`, `dependencies()`, `initialize()`. |
| `knowit/__main__.py` | CLI (argparse). Calls `api.know()`. Also has `--report`, `--bug-report`, `--check-name`, and `--collect`. |
| `knowit/bugreport.py` | Builds and redacts the `--bug-report` file. |
| `knowit/collect.py` | `--collect`: builds the record of each file (the redacted output of each provider), writes the records to JSON Lines parts, and resumes a stopped run. |
| `knowit/config.py` | Loads `knowit/defaults.yml` and an optional user config into a `Config` object. |
| `knowit/core.py` | Base classes: `Reportable`, `Property`, `Configurable`, `MultiValue`, `Rule`. |
| `knowit/environment.py` | Collects the environment information for bug reports. |
| `knowit/pathcheck.py` | `--check-name`: probes a generated sample under the name of the reporter's file. |
| `knowit/provider.py` | `Provider` and `Executor` base classes for all backends, and the provider errors. |
| `knowit/serializer.py` | YAML and JSON dump helpers, custom YAML loader and dumper. |
| `knowit/units.py` | pint `UnitRegistry` wrapper. Uses `NullRegistry` when pint is not installed. |
| `knowit/utils.py` | Path helpers and OS detection. |
| `knowit/defaults.yml` | The knowledge base: codecs, profiles, and other known values. See `docs/knowledge-base.md`. |
| `knowit/properties/` | `Property` subclasses. Each one describes one field (codec, language, ...). |
| `knowit/providers/` | One module for each backend: `mediainfo.py`, `ffmpeg.py`, `mkvmerge.py`, `enzyme.py`. |
| `knowit/rules/` | `Rule` subclasses. Each one derives or corrects fields after extraction. |

## Lookup flow

1. `api.know(path, context)` finds the first `Provider` whose `accepts()` returns true.
2. It calls `describe()`. `describe()` calls `Provider._describe_tracks()`, which calls
   `_describe_track()` for each track.
3. The provider `mapping` gives the fields of each track. The mapping is a dict of `Property` or
   `Configurable` instances, keyed by the output field name. `None` is a placeholder for a field that a
   `Rule` fills in.
4. The provider `rules` run on the result.

## Base classes

- `Property`: extracts and transforms one field from the raw track data. Examples: `Quantity` adds a unit,
  `Duration` parses timestamps, `Basic` converts to a data type.
- `Configurable`: a `Property` that gets its result from a lookup table in `knowit/defaults.yml`, through
  `Config.<ClassName>`. `_extract_key()` gives the lookup key. `_extract_fallback_key()` lets a subclass
  try again with a less specific key. Example: `AudioCodec` removes all text after a `/`.
- `Rule`: runs after all properties of a track. It gets the `props` and `pv_props` dicts and can add,
  change, or delete fields. Examples: `ResolutionRule` derives `1080p` from the width, the height, and the
  aspect ratio. `AtmosRule` changes the codec when it finds Dolby Atmos.
- `Executor`: runs the external process or library call. Examples: `MediaInfoCliExecutor` runs the
  `mediainfo` binary. `MediaInfoCTypesExecutor` loads `libmediainfo` with ctypes. `NotFoundExecutor`
  stands in when nothing is installed. Its `__bool__` always returns `False`. `Provider.loaded()` uses
  this to find it.

## Errors

- Providers raise `ProviderError`, `MalformedFileError`, or `UnsupportedFileFormatError`.
- The CLI executors run the backend with `run_command()` in `knowit/provider.py`. When the backend
  fails, it raises `ProviderError` with the message of the backend.
- `api.know()` catches every error and raises `KnowitException`. Its message is `debug_info()`, which is
  the text for a bug report.

## Public API

Other applications, for example Bazarr, Medusa, and subliminal, use knowit as a library. The public names
are `know()`, `dependencies()`, `initialize()`, and `KnowitException`, all exported from `knowit/api.py`.
`know()` returns a mapping of metadata, or `{}` when no provider can read the file. Do not remove or
rename these names, and do not change their signatures, without a major version.
