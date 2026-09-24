# Knowledge base

`knowit/defaults.yml` holds the values that knowit knows: codecs, profiles, scan types, and more.
`Config.build()` in `knowit/config.py` loads it.

## Format

The file has two top-level sections.

- `knowledge`: for each `Configurable` class name (`VideoCodec`, `AudioCodec`, ...), a map from a canonical
  code to the list of raw values that the backends report for it.
- `profiles`: for each class name and code, the names to show: `default`, `human`, and `technical`. A
  missing name takes the value of the previous one (`code`, then `default`, then `human`).

```yaml
knowledge:
  VideoCodec:
    MPEG2:
      - MPEG2
      - MPEG-2V

profiles:
  VideoCodec:
    MPEG2:
      default: MPEG-2
      human: MPEG-2 Video
      technical: MPEG-2 Part 2
```

The special code `__ignored__` lists raw values that knowit skips. It does not return them and does not
warn about them.

A user config file (the `config` context key) uses the same format. A class section in the user file
replaces the complete default section of that class.

## Add a value

1. Get the raw value. `knowit --report <path>` lists every value that knowit does not know. The
   "Unknown or missing value" issue template asks the reporter for this output.
2. Add the raw value to the list of the correct code under `knowledge`. For a new code, also add its names
   under `profiles`.
3. Add a test case. See `docs/testing.md`.
