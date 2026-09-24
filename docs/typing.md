# Typing

`[tool.mypy]` in `pyproject.toml` sets `strict = true`. The code has no mypy errors. Keep it that way.

The backends give raw data with no type. Some patterns come back because of this.

## `Property.handle` takes `typing.Any`

In `Property[T]`, `T` is the type that `handle()` returns (the parsed result). It is not the type that
`handle()` gets. The input is always raw track data from mediainfo, ffprobe, mkvmerge, or enzyme. For this
reason, the `value` parameter of `Property.handle` in `knowit/core.py` is `typing.Any`. Do not change it
back to `T`.

One exception exists: `Configurable.handle` declares `value: T` and then uses
`typing.cast(str, value)`, because its lookups always use a string key.

## `_extract_key` returns `Literal[False]`

`Configurable._extract_key` returns `str | typing.Literal[False]`, not `str | bool`. `False` is a sentinel
that means "skip the lookup, do not warn". The function never returns `True`. With `Literal[False]`, mypy
narrows the result to `str` after an `is False` check. With `bool`, a `Literal[True]` case stays.

## `Config` is a dynamic attribute bag

`Config.build()` in `knowit/config.py` replaces `self.__dict__` with sections keyed by class name
(`AudioCodec`, `VideoCodec`, `ScanType`, ...). The data comes from `knowit/defaults.yml`. `Config` declares
`__getattr__(self, item: str) -> typing.Any` only so that mypy accepts access such as `config.AudioCodec`.
Do not add real attributes for IDE completion.

## mypy runs for Linux

`platform = "linux"` in `pyproject.toml`. CI (`ubuntu-latest`) and the Docker image run on Linux. With this
setting, a contributor on Windows or macOS gets the same mypy errors as CI. This matters for stubs that
change with the platform. Example: `ctypes.WinDLL` in `knowit/providers/mediainfo.py` has a
`# type: ignore[attr-defined]`. The ignore is only necessary on the Linux platform.
