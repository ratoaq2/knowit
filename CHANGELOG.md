# Changelog

The notes for older versions are in the [GitHub releases](https://github.com/ratoaq2/knowit/releases).

## Unreleased

- New `--collect` mode. It writes the output of every provider for each file of a media library, to help
  improve knowit. Titles are masked. A stopped scan continues where it stopped. `--deep` also reads the
  HDR10+ and Dolby Vision data of the first video frames with ffprobe.
- A redacted `--bug-report` now keeps the technical ffprobe tags, such as the track language. Before, it
  masked them with the titles.
- A redacted `--bug-report` now masks the mediainfo encoder version, for example `x265 - 3.3+4-group`.
  A custom encoder build can put the name of a release group in it.
- A redacted `--bug-report` now masks the Matroska segment and track uids, and the encoding, tagging, and
  file dates. Before, they could identify the file.
- A redacted `--bug-report` now masks the enzyme track names and chapter names. Before, a title in these
  names stayed readable.
- A redacted `--bug-report` now masks the path in the error messages of the backends, and the folder of
  the last file of a Blu-ray playlist (mediainfo `FolderName_Last`).
- A redacted `--bug-report` now masks the non-ascii letters and digits, for example a title in Cyrillic or
  Japanese. Before, they stayed readable in the titles and in the path.

- When ffprobe, mediainfo, or mkvmerge fails, the error now shows the message of the backend, not only the
  exit status. ([#44](https://github.com/ratoaq2/knowit/issues/44))
- A language value that is not a string no longer stops the analysis of the file. knowit reports it and
  uses `und`. ([#219](https://github.com/ratoaq2/knowit/issues/219))
- When mediainfo cannot open a file, knowit now raises a provider error with a clear message. If the name
  is not ascii and the locale is not UTF-8, the message tells you to set `LANG=C.UTF-8`.
  ([#200](https://github.com/ratoaq2/knowit/issues/200))
