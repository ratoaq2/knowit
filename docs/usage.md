# Usage details

This page is the reference for the knowit command and the Python library. The
[README](../README.md) gives the quick start and the common scenarios.

## All options

```text
$ knowit --help
usage: knowit [-h] [-p PROVIDER] [--debug] [--report] [-y] [-N] [-P PROFILE]
              [--mediainfo MEDIAINFO] [--ffmpeg FFMPEG] [--mkvmerge MKVMERGE]
              [--bug-report] [--bug-report-output FILE] [--no-redact]
              [--check-name NAME] [--collect] [-o FILE] [--deep] [--version]
              [videopath ...]

positional arguments:
  videopath             Path to the video to introspect

options:
  -h, --help            show this help message and exit

Providers:
  -p, --provider PROVIDER
                        The provider to be used: mediainfo, ffmpeg, mkvmerge
                        or enzyme.

Output:
  --debug               Print information for debugging knowit and for
                        reporting bugs.
  --report              Parse media and report all non-detected values
  -y, --yaml            Display output in yaml format
  -N, --no-units        Display output without units
  -P, --profile PROFILE
                        Display values according to specified profile: code,
                        default, human, technical

Configuration:
  --mediainfo MEDIAINFO
                        The location to search for MediaInfo binaries
  --ffmpeg FFMPEG       The location to search for ffprobe (FFmpeg) binaries
  --mkvmerge MKVMERGE   The location to search for mkvmerge (MKVToolNix)
                        binaries

Bug reporting:
  --bug-report          Write a report with the environment and the raw output
                        of every provider, to attach to an issue.
  --bug-report-output FILE
                        Where to write the bug report. Use - to write it to
                        the standard output.
  --no-redact           Do not mask titles, file names and tags in the bug
                        report or the collected data.
  --check-name NAME     Check whether a file name makes a provider fail. No
                        media file is needed.

Collect:
  --collect             Write the output of every provider for each file, to
                        improve knowit. Use --no-redact to keep titles.
  -o, --collect-output FILE
                        Where to write the collected data, default knowit-
                        collect.jsonl.gz. A run continues an existing file.
  --deep                Also read the first video frames with ffprobe, for
                        HDR10+ and Dolby Vision data. Slower.

Information:
  --version             Display knowit version.
```

The bug report options and `--collect` are in
[Troubleshooting](troubleshooting.md).

## Providers

A provider is the program that knowit uses to read the file. knowit uses the first installed provider that
accepts the file, in this order:

| Provider | Program | Files | Notes |
| --- | --- | --- | --- |
| `mediainfo` | [MediaInfo](https://mediaarea.net/MediaInfo) | All video files | Gives the most information. |
| `ffmpeg` | ffprobe, from [FFmpeg](https://ffmpeg.org/download.html) | All video files | |
| `mkvmerge` | mkvmerge, from [MKVToolNix](https://mkvtoolnix.download/downloads.html) | `.mkv`, `.mka`, `.mks` | |
| `enzyme` | Included in knowit | `.mkv` | Gives less information. |

To use one provider only, give `-p`, for example `knowit -p ffmpeg movie.mkv`.

### Install the providers

On most systems, knowit installs the MediaInfo library with the
[pymediainfo](https://github.com/sbraz/pymediainfo) package. You do not need to install more programs.

If your system has no MediaInfo library, or if you want other providers, install the programs:

**Ubuntu, Debian, and WSL**

```bash
sudo apt-get install mediainfo ffmpeg mkvtoolnix
```

**Windows** (with [Chocolatey](https://chocolatey.org/))

```bash
choco install mediainfo ffmpeg mkvtoolnix
```

**macOS** (with [Homebrew](https://brew.sh/))

```bash
brew install media-info ffmpeg mkvtoolnix
```

### Find the providers

knowit looks for the programs in some common folders and in the `PATH`. If a program is in a different
folder, give the folder or the program file:

```bash
knowit --mediainfo /opt/mediainfo --ffmpeg /opt/ffmpeg --mkvmerge /opt/mkvtoolnix movie.mkv
```

`knowit --version` shows the knowit version, the Python version, and each provider that knowit finds:

```text
providers:
  mediainfo:
    pymediainfo: 7.0.1
    libmediainfo.so.0: v25.4
  ffmpeg:
    ffprobe: v7.1.5-0+deb13u1
  mkvmerge:
    mkvmerge: v92.0
  enzyme:
    enzyme: 0.5.2
```

## Profiles

A profile changes how knowit shows the values. The same file with each profile:

| Profile | `duration` | `size` | `bit_rate` |
| --- | --- | --- | --- |
| `default` | `0:00:46` | `31.76 MB` | `5.4 Mbps` |
| `human` | `46 seconds` | `31.76 MB` | `5.4 Mbps` |
| `technical` | `'0:00:46.665000'` | `30.291 MiB` | `5.193 Mibps` |
| `code` | `'46.665'` | `31762747` | `5445237` |

The profile also changes the text values. For example, the video codec of the same file is
`Advanced Video Coding (H.264)` with `human`, and `H.264` with `default`.

## Units

The `pint` extra (`knowit[pint]`) adds units to the values, for example `31.76 MB` or `1024 pixel`.
Without it, knowit shows plain numbers.

`-N` (`--no-units`) shows plain numbers also when `pint` is installed:

```text
$ knowit -y -N movie.mkv
...
  duration: 0:00:46
  size: 31762747
  bit_rate: 5445237
```

## Python API

```python
from knowit import know

info = know('/medias/movie.mkv')
print(info['video'][0]['codec'])  # H.264

info = know('/medias/movie.mkv', {'provider': 'ffmpeg', 'profile': 'code'})
print(info['video'][0]['codec'])  # H264
```

`know(path, options)` returns a `dict`. It returns `{}` when no provider can read the file. The values are
Python objects, for example a `datetime.timedelta` for `duration`, and a `pint` quantity for `size` when
`pint` is installed.

The options `dict` has the same keys as the command options:

| Key | Command option |
| --- | --- |
| `provider` | `-p`, `--provider` |
| `profile` | `-P`, `--profile` |
| `no_units` | `-N`, `--no-units` |
| `mediainfo`, `ffmpeg`, `mkvmerge` | `--mediainfo`, `--ffmpeg`, `--mkvmerge` |

`know` raises `KnowitException` when knowit cannot read the file. The message is the debug information for a
bug report. The [architecture](architecture.md#public-api) page gives the contract of the public API.

## Docker

The [Docker image](https://hub.docker.com/r/ratoaq2/knowit) contains knowit with the `pint` extra,
MediaInfo, FFmpeg, and MKVToolNix. Mount the folder of your media, and give the path in the container:

```bash
docker run -it --rm -v /medias:/medias ratoaq2/knowit /medias/movie.mkv
```

All the options work in the same way, for example:

```bash
docker run -it --rm -v /medias:/medias ratoaq2/knowit -y -P human /medias/movie.mkv
```
