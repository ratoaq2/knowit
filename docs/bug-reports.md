# Bug reports

Users cannot send their media, and the maintainer cannot reproduce a bug without it. The report flow does
not need the media.

## Flow

```bash
# What the reporter runs. Writes knowit-report.yml: environment, path diagnostics,
# and the raw output of every installed backend, with titles masked.
knowit --bug-report /path/to/video.mkv

# For "cannot open this file" reports, which are mostly about the name, not the
# content. Probes a generated Matroska sample under that name and under an ascii
# control name, then says which backend fails only because of the name.
knowit --check-name "The Accountant² (2025).mkv"

# What the maintainer runs on the attached file. Writes tests/data/<provider>/
# issue-220-example.mkv.{json,yml} for every backend that produced output.
uv run python scripts/import_report.py knowit-report.yml --issue 220
uv run pytest tests -k issue-220
```

The importer sends the raw data through the current code to make the `.yml` file. Thus the new fixture
agrees with the current code. For a wrong value, first correct the `.yml` file to the expected values.
The test then fails until the bug is fixed.

## Modules

- `knowit/environment.py` collects the environment.
- `knowit/bugreport.py` builds and redacts the report. Redaction is on by default. `--no-redact` turns it
  off. Redaction masks all values in the ffprobe `tags` and the mediainfo `extra` blocks, except the
  technical keys in `TECHNICAL_TAG_KEYS`. knowit reads these keys, for example the track language.
  `mask_path()` also masks the path, its folder, and its file name in every string of the provider
  results. The error messages of the backends quote the path.
  The mediainfo encoder version (`Encoded_Library`) is masked. A custom encoder build can put the name of
  a release group in it. `Encoded_Library_Name` stays readable, because knowit reads it.
  The unique ids (Matroska segment and track uids) and the dates (encoding, tagging, and file dates) are
  masked. They identify one file, and the file dates tell when the user got it.
  `mask_text()` masks the letters and digits of every script. A non-ascii title identifies the media too.
  Symbols and combining marks stay readable. In the path description, `non_ascii` names only these
  symbols. It shows the masked letters and digits as `non-ascii letter` and `non-ascii number`.
- `knowit/pathcheck.py` does the name check. `ADVERSARIAL_NAMES` in that file is the regression list of
  names from real issues. Add a name when a new one comes in.
- `.github/ISSUE_TEMPLATE/` asks the reporter for these commands.

## Limits of `--check-name`

`--check-name` proves something only for a name that stays valid Unicode text from the shell to the
process. This includes accents, CJK, emoji, symbols, and NFC/NFD differences.

It cannot reproduce an invalid byte sequence, for example a name from a non-Unicode codepage. Nobody can
type such bytes, paste them into an issue, or give them to `docker run`, because all of these need valid
UTF-8. The Docker CLI changes invalid bytes in its arguments to U+FFFD before the container gets them.

If a name looks like mojibake, or the reporter cannot type it correctly, ask for `--bug-report` on the real
file. It finds the name with `os.scandir`, which keeps undecodable bytes as lone surrogates.

`--check-name` can also show a locale mismatch. Under the C locale, Python uses UTF-8 for file names (UTF-8
mode), but the C library does not. knowit creates the file, and mediainfo and mkvmerge cannot open it
(issue #200). ffprobe and enzyme can open it. The mediainfo error tells the user to set `LANG=C.UTF-8`:

```bash
LC_ALL=C knowit --check-name "Café.mkv"
```

With `PYTHONUTF8=0` added, knowit cannot create a file with a non-ascii name.
