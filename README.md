<h1 align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/ratoaq2/knowit/main/docs/images/logo-dark.png">
    <img alt="knowit: Know your media" src="https://raw.githubusercontent.com/ratoaq2/knowit/main/docs/images/logo-light.png" width="400">
  </picture>
</h1>

knowit reads the metadata of video files with MediaInfo, ffprobe, mkvmerge, or enzyme, and gives it in one
format.

[![PyPI version](https://img.shields.io/pypi/v/knowit.svg)](https://pypi.org/project/knowit/)
[![Python versions](https://img.shields.io/pypi/pyversions/knowit.svg)](https://pypi.org/project/knowit/)
[![Tests](https://github.com/ratoaq2/knowit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/knowit/actions/workflows/test.yml)
[![Docker pulls](https://img.shields.io/docker/pulls/ratoaq2/knowit.svg)](https://hub.docker.com/r/ratoaq2/knowit)
[![License](https://img.shields.io/github/license/ratoaq2/knowit.svg)](https://github.com/ratoaq2/knowit/blob/main/LICENSE)

![knowit shows the video, audio, and subtitle tracks of a .mkv file](https://raw.githubusercontent.com/ratoaq2/knowit/main/docs/images/demo.gif)

## Why knowit

Different tools give video metadata in different formats and with different names. knowit reads the
output of MediaInfo, ffprobe, mkvmerge, or enzyme. It gives the result in one format, with the same names
and units for all of them. You can use knowit as a command or as a Python library.

## What knowit gives

knowit gives the general properties of the file, and the properties of each video, audio, and subtitle
track. Some examples:

| Part | Examples |
| --- | --- |
| General | `title`, `duration`, `size`, `bit_rate`, `container` |
| Video | `codec`, `resolution`, `frame_rate`, `hdr_format`, `bit_depth` |
| Audio | `codec`, `channels`, `language`, `commentary` |
| Subtitle | `format`, `language`, `forced`, `hearing_impaired` |

Each provider gives a different set of properties. The full list for each provider is in
[`knowit/providers/`](https://github.com/ratoaq2/knowit/tree/main/knowit/providers).

## Quick start

1. Install knowit:

   ```bash
   uv tool install "knowit[pint]"
   ```

2. Read a video:

   ```text
   $ knowit -y -P human movie.mkv
   ...
   movie.mkv:
     title: Big Buck Bunny - test 8
     path: movie.mkv
     duration: 46 seconds
     size: 31.76 MB
     bit_rate: 5.4 Mbps
     container: mkv
     video:
     - id: 1
       width: 1024 pixel
       height: 576 pixel
       resolution: 576p
       frame_rate: 24.0 FPS
       codec: Advanced Video Coding (H.264)
       ...
     audio:
     - id: 2
       codec: Advanced Audio Coding
       channels: '2.0'
       sampling_rate: 48.0 KHz
       ...
     subtitle:
     - id: 3
       language: English
       format: SubRip
       default: true
     ...
   ```

To try knowit without installing it, use `uvx knowit movie.mkv`.

## Installation

### Install knowit

Use one of these commands:

| Command | When to use it |
| --- | --- |
| `uv tool install "knowit[pint]"` | Recommended. [uv](https://docs.astral.sh/uv/getting-started/installation/) also installs Python if necessary. |
| `pipx install "knowit[pint]"` | You already use [pipx](https://pipx.pypa.io/). |
| `pip install knowit` | You want to use knowit as a Python library. |

The `pint` extra adds units to the values, for example `31.76 MB` or `1024 pixel`. Without it, knowit
shows plain numbers.

To upgrade, use `uv tool upgrade knowit` or `pipx upgrade knowit`.

### Providers

A provider is the program that knowit uses to read the file: `mediainfo` (the default), `ffmpeg`,
`mkvmerge`, or `enzyme`. On most systems, knowit installs the MediaInfo library with the
[pymediainfo](https://github.com/sbraz/pymediainfo) package, and you do not need to install more programs.

To see which providers knowit finds, run `knowit --version`. To install other providers, see
[Providers](https://github.com/ratoaq2/knowit/blob/main/docs/usage.md#providers).

### Docker

The [Docker image](https://hub.docker.com/r/ratoaq2/knowit) contains knowit and all the providers:

```bash
docker run -it --rm -v /medias:/medias ratoaq2/knowit /medias/movie.mkv
```

## Usage

Read a video with a specific provider:

```bash
knowit -p ffmpeg movie.mkv
```

Show the result in YAML. The default is JSON:

```bash
knowit -y movie.mkv
```

Show the values with a profile: `default`, `human`, `technical`, or `code`:

```text
$ knowit -y -P human movie.mkv        $ knowit -y -P technical movie.mkv
  duration: 46 seconds                  duration: '0:00:46.665000'
  size: 31.76 MB                        size: 30.291 MiB
  bit_rate: 5.4 Mbps                    bit_rate: 5.193 Mibps
```

Show the values without units:

```bash
knowit -N movie.mkv
```

Read all the videos of a folder, and list the values that knowit does not know:

```bash
knowit --report /path/to/your/media
```

Use knowit in Python:

```python
from knowit import know

info = know('/medias/movie.mkv', {'provider': 'ffmpeg'})
print(info['video'][0]['codec'])  # H.264
```

### Main options

| Option | What it does |
| --- | --- |
| `-p`, `--provider` | Use this provider: `mediainfo`, `ffmpeg`, `mkvmerge`, or `enzyme`. |
| `-y`, `--yaml` | Show the result in YAML. The default is JSON. |
| `-P`, `--profile` | Show the values with this profile: `default`, `human`, `technical`, or `code`. |
| `-N`, `--no-units` | Show the values without units. |
| `--mediainfo`, `--ffmpeg`, `--mkvmerge` | Look for the program in this folder. |
| `--report` | Read a folder and list the values that knowit does not know. |
| `--bug-report` | Write a file to attach to an issue. See [Report a bug](#report-a-bug). |
| `--version` | Show the knowit version and the providers that knowit finds. |

[Usage details](https://github.com/ratoaq2/knowit/blob/main/docs/usage.md) gives all the options, the
profiles, and the Python API.

## FAQ

**Which provider should I use?**
Use MediaInfo if you can. It gives the most information.

**knowit gives a wrong value. What can I do?**
Try another provider with `-p`. Then [report a bug](#report-a-bug), and tell which providers give the
wrong value.

**Which files does knowit read?**
With MediaInfo or ffprobe, knowit reads all common video files, for example `.mkv`, `.mp4`, `.avi`, and
`.ts`. With only mkvmerge or enzyme, knowit reads only Matroska files (`.mkv`).

**Does knowit send my files or file names anywhere?**
No. knowit reads the files on your computer. It does not use the network. A bug report or a collect file
leaves your computer only when you attach it to an issue.

## Report a bug

Do not send your media file. Run this command instead, and attach `knowit-report.yml` to an
[issue](https://github.com/ratoaq2/knowit/issues):

```bash
knowit --bug-report "/path/to/your/video.mkv"
```

The report contains the output of every provider. Titles, file names, and free-text tags are masked.

When the problem is the name of the file, use `knowit --check-name "The Accountant² (2025).mkv"`. It
tells you which provider fails because of the name.

[Troubleshooting](https://github.com/ratoaq2/knowit/blob/main/docs/troubleshooting.md) gives all the
details.

## Help to improve knowit

knowit is more correct when it sees many different files. Run this command on your library, and attach
the files that it writes to an [issue](https://github.com/ratoaq2/knowit/issues):

```bash
knowit --collect /path/to/your/media
```

Your media is not needed. Titles and file names are masked. See
[Help to improve knowit](https://github.com/ratoaq2/knowit/blob/main/docs/troubleshooting.md#help-to-improve-knowit).

## Used by

- [Subliminal](https://github.com/Diaoul/subliminal)
- [Bazarr](https://github.com/morpheus65535/bazarr)
- [Medusa](https://github.com/pymedusa/Medusa)

## Contributing

Read [CONTRIBUTING.md](https://github.com/ratoaq2/knowit/blob/main/CONTRIBUTING.md) before you open a pull
request.

## License

[MIT](https://github.com/ratoaq2/knowit/blob/main/LICENSE).

The knowit name, logo, and icon are not covered by the MIT license. All rights reserved.
