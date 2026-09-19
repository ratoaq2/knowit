# KnowIt

Know better your media files.

[![Latest
Version](https://img.shields.io/pypi/v/knowit.svg)](https://pypi.python.org/pypi/knowit)

[![tests](https://github.com/ratoaq2/knowit/actions/workflows/test.yml/badge.svg)](https://github.com/ratoaq2/knowit/actions/workflows/test.yml)

[![License](https://img.shields.io/github/license/ratoaq2/knowit.svg)](https://github.com/ratoaq2/knowit/blob/master/LICENSE)

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/knowit)

  - Project page  
    <https://github.com/ratoaq2/knowit>

## Usage

### CLI

Extract information from a video file:

    $ knowit /folder/Audio Samples/hd_dtsma_7.1.mkv
    For: /folder/Audio Samples/hd_dtsma_7.1.mkv
    Knowit 0.4.0 found:
    {
        "title": "7.1Ch DTS-HD MA - Speaker Mapping Test File",
        "path": "/folder/Audio Samples/hd_dtsma_7.1.mkv",
        "duration": "0:01:37",
        "size": "40.77 MB",
        "bit_rate": "3.3 Mbps",
        "container": "mkv",
        "video": [
            {
                "id": 1,
                "duration": "0:01:37",
                "width": "1920 pixel",
                "height": "1080 pixel",
                "scan_type": "Progressive",
                "aspect_ratio": "1.778",
                "pixel_aspect_ratio": "1.0",
                "resolution": "1080p",
                "frame_rate": "23.976 FPS",
                "bit_depth": "8 bit",
                "codec": "H.264",
                "profile": "Main",
                "profile_level": "4",
                "media_type": "video/H264",
                "default": true
            }
        ],
        "audio": [
            {
                "id": 2,
                "name": "7.1Ch DTS-HD MA",
                "language": "English",
                "duration": "0:01:37",
                "codec": "DTS-HD",
                "profile": "Master Audio",
                "channels_count": 8,
                "channels": "7.1",
                "bit_depth": "24 bit",
                "bit_rate_mode": "Variable",
                "sampling_rate": "48.0 KHz",
                "compression": "Lossless",
                "default": true
            }
        ],
        "provider": {
            "name": "mediainfo",
            "version": {
                "pymediainfo": "5.0.3",
                "libmediainfo.so.0": "v20.9"
            }
        }
    }

Extract information from a video file using ffmpeg:

    $ knowit --provider ffmpeg /folder/Audio Samples/hd_dtsma_7.1.mkv
    For: /folder/Audio Samples/hd_dtsma_7.1.mkv
    Knowit 0.4.0 found:
    {
        "title": "7.1Ch DTS-HD MA - Speaker Mapping Test File",
        "path": "/folder/Audio Samples/hd_dtsma_7.1.mkv",
        "duration": "0:01:37",
        "size": "40.77 MB",
        "bit_rate": "3.3 Mbps",
        "container": "mkv",
        "video": [
            {
                "id": 0,
                "width": "1920 pixel",
                "height": "1080 pixel",
                "scan_type": "Progressive",
                "aspect_ratio": "1.778",
                "pixel_aspect_ratio": "1.0",
                "resolution": "1080p",
                "frame_rate": "23.976 FPS",
                "bit_depth": "8 bit",
                "codec": "H.264",
                "profile": "Main",
                "default": true
            }
        ],
        "audio": [
            {
                "id": 1,
                "name": "7.1Ch DTS-HD MA",
                "language": "English",
                "codec": "DTS-HD",
                "profile": "Master Audio",
                "channels_count": 8,
                "channels": "7.1",
                "bit_depth": "24 bit",
                "sampling_rate": "48.0 KHz",
                "default": true
            }
        ],
        "provider": {
            "name": "ffmpeg",
            "version": {
                "ffprobe": "v4.2.4-1ubuntu0.1"
            }
        }
    }

Using docker:

    docker run -it --rm -v /folder:/folder knowit /folder/Audio Samples/hd_dtsma_7.1.mkv
    For: /folder/Audio Samples/hd_dtsma_7.1.mkv
    Knowit 0.4.0 found:
    {
        "title": "7.1Ch DTS-HD MA - Speaker Mapping Test File",
        "path": "/folder/Audio Samples/hd_dtsma_7.1.mkv",
        "duration": "0:01:37",
        "size": "40.77 MB",
        "bit_rate": "3.3 Mbps",
        "container": "mkv",
        "video": [
            {
                "id": 1,
                "duration": "0:01:37",
                "width": "1920 pixel",
                "height": "1080 pixel",
                "scan_type": "Progressive",
                "aspect_ratio": "1.778",
                "pixel_aspect_ratio": "1.0",
                "resolution": "1080p",
                "frame_rate": "23.976 FPS",
                "bit_depth": "8 bit",
                "codec": "H.264",
                "profile": "Main",
                "profile_level": "4",
                "media_type": "video/H264",
                "default": true
            }
        ],
        "audio": [
            {
                "id": 2,
                "name": "7.1Ch DTS-HD MA",
                "language": "English",
                "duration": "0:01:37",
                "codec": "DTS-HD",
                "profile": "Master Audio",
                "channels_count": 8,
                "channels": "7.1",
                "bit_depth": "24 bit",
                "bit_rate_mode": "Variable",
                "sampling_rate": "48.0 KHz",
                "compression": "Lossless",
                "default": true
            }
        ],
        "provider": {
            "name": "mediainfo",
            "version": {
                "pymediainfo": "5.0.3",
                "libmediainfo.so.0": "v20.9"
            }
        }
    }

All available CLI options:

    $ knowit --help
    usage: knowit [-h] [-p PROVIDER] [--debug] [--report] [-y] [-N] [-P PROFILE] [--mediainfo MEDIAINFO]
                  [--ffmpeg FFMPEG] [--mkvmerge MKVMERGE] [--bug-report] [--bug-report-output FILE]
                  [--no-redact] [--check-name NAME] [--version] [videopath ...]

    positional arguments:
      videopath             Path to the video to introspect

    options:
      -h, --help            show this help message and exit

    Providers:
      -p, --provider PROVIDER
                            The provider to be used: mediainfo, ffmpeg, mkvmerge or enzyme.

    Output:
      --debug               Print information for debugging knowit and for reporting bugs.
      --report              Parse media and report all non-detected values
      -y, --yaml            Display output in yaml format
      -N, --no-units        Display output without units
      -P, --profile PROFILE
                            Display values according to specified profile: code, default, human, technical

    Configuration:
      --mediainfo MEDIAINFO
                            The location to search for MediaInfo binaries
      --ffmpeg FFMPEG       The location to search for ffprobe (FFmpeg) binaries
      --mkvmerge MKVMERGE   The location to search for mkvmerge (MKVToolNix) binaries

    Bug reporting:
      --bug-report          Write a report with the environment and the raw output of every provider, to
                            attach to an issue.
      --bug-report-output FILE
                            Where to write the bug report. Use - to write it to the standard output.
      --no-redact           Do not mask titles, file names and tags in the bug report.
      --check-name NAME     Check whether a file name makes a provider fail. No media file is needed.

    Information:
      --version             Display knowit version.

## Reporting a problem

Do not send your media file. It is not needed, and it is usually too large.
Run this command instead:

    $ knowit --bug-report "/path/to/your/video.mkv"
    Bug report written to knowit-report.yml

Attach `knowit-report.yml` to an issue at
<https://github.com/ratoaq2/knowit/issues>.

The report contains:

- the knowit version, and where knowit is installed from
- the Python version, the operating system, and the text encodings in use
- the location and version of MediaInfo, ffprobe, mkvmerge and enzyme
- the characters of the file path, with their Unicode names
- the raw output of every installed provider for that file
- the values knowit parsed from that output, or the error it failed with

Titles, file names and tags are masked. Non-ascii characters are kept, because
they are often the cause of the problem. Use `--no-redact` to keep the original
text.

If knowit is bundled in another application, such as Bazarr or Medusa, run the
command with the same Python that runs that application:

    $ python -m knowit --bug-report "/path/to/your/video.mkv"

If a codec, a profile or another value is not known by knowit, use `--report`
instead. It accepts a directory and lists every value knowit does not know:

    $ knowit --report /path/to/your/media

### Problems with a file name

Many problems come from the name of the file, not from its content: a superscript,
a fraction, an accent, or a character the file system encoding cannot represent.
For those, only the name is needed:

    $ knowit --check-name "The Accountant² (2025).mkv"

knowit writes a small generated Matroska file under that name, and also under a
plain ascii name. It then compares the two results:

    result:
      mediainfo: ok: the name is handled correctly
      ffmpeg: ok: the name is handled correctly
      mkvmerge: ok: the name is handled correctly
      enzyme: fails with this name only: the name is the problem

A provider that fails only with your name has a name handling problem. A provider
that fails with both names has a problem with the file content instead.

Add a file to use your own media as the sample:

    $ knowit --check-name "The Accountant² (2025).mkv" /path/to/any/video.mkv

## Installation

KnowIt can be installed as a regular python module by running:

    $ [sudo] pip install knowit

For a better isolation with your system you should use a dedicated
virtualenv or install for your user only using the `--user` flag.

## External dependencies

KnowIt can use MediaInfo, ffprobe (FFmpeg) or mkvmerge (MKVToolNix)

KnowIt supports MKV regardless if MediaInfo, FFmpeg or MKVToolNix are
installed.

MediaInfo, FFmpeg or MKVToolNix increases the number of supported
formats and the number of extracted information.

MediaInfo is the default provider. Visit their
[website](http://mediaarea.net/MediaInfo) and install the proper package
for your system.

ffprobe (FFmpeg) can be downloaded
[here](https://ffmpeg.org/download.html)

mkvmerge (MKVToolNix) can be downloaded
[here](https://mkvtoolnix.download/downloads.html)
