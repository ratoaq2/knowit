# Changelog

The notes for older versions are in the [GitHub releases](https://github.com/ratoaq2/knowit/releases).

## Unreleased

- When ffprobe, mediainfo, or mkvmerge fails, the error now shows the message of the backend, not only the
  exit status. ([#44](https://github.com/ratoaq2/knowit/issues/44))
- A language value that is not a string no longer stops the analysis of the file. knowit reports it and
  uses `und`. ([#219](https://github.com/ratoaq2/knowit/issues/219))
