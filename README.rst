KnowIt
==========
Know better your media files.

.. image:: https://img.shields.io/pypi/v/knowit.svg
    :target: https://pypi.python.org/pypi/knowit
    :alt: Latest Version

.. image:: https://travis-ci.org/ratoaq2/knowit.svg?branch=master
    :target: https://travis-ci.org/ratoaq2/knowit
    :alt: Travis CI build status

.. image:: https://img.shields.io/github/license/ratoaq2/knowit.svg
    :target: https://github.com/ratoaq2/knowit/blob/master/LICENSE
    :alt: License


:Project page: https://github.com/ratoaq2/knowit


Usage
-----
CLI
^^^
Extract information from a video file::

    $ knowit FooBar.mkv
    For: FooBar.mkv
    {
        "title": "Foo.Bar",
        "path": "/folder/FooBar.mkv",
        "duration": "2:06:09.001000",
        "size": "611.24 MB",
        "bit_rate": "1.8 Mbps",
        "video": [
            {
                "number": 1,
                "language": "English",
                "duration": "2:06:09.012000",
                "width": "1920 pixel",
                "height": "796 pixel",
                "scan_type": "Progressive",
                "aspect_ratio": 2.412,
                "pixel_aspect_ratio": 1.0,
                "resolution": "1080p",
                "frame_rate": "23.976 FPS",
                "bit_depth": "8 bit",
                "codec": "H.264",
                "profile": "High@L4.1",
                "encoder": "x264",
                "media_type": "video/H264",
                "default": true
            }
        ],
        "audio": [
            {
                "number": 2,
                "name": "DTS MA 5.1 16bit",
                "language": "English",
                "duration": "2:06:09.001000",
                "codec": "DTS-HD Master Audio",
                "channels_count": 6,
                "channels": "5.1",
                "bit_rate": [
                    null,
                    "1509.0 Kbps"
                ],
                "bit_rate_mode": [
                    "Variable",
                    "Constant"
                ],
                "sampling_rate": "48.0 KHz",
                "compression": [
                    "Lossless",
                    "Lossy"
                ],
                "default": true
            },
            {
                "number": 3,
                "name": "DD5.1 448Kbps",
                "language": "Chinese",
                "duration": "2:06:09.001000",
                "size": 448.01 MB,
                "codec": "AC3",
                "channels_count": 6,
                "channels": "5.1",
                "bit_rate": "448 Kbps",
                "bit_rate_mode": "Constant",
                "sampling_rate": "48.0 KHz",
                "compression": "Lossy"
            }
        ],
        "subtitle": [
            {
                "number": 4,
                "language": "English",
                "format": "SubRip",
                "encoding": "UTF-8",
                "default": true
            }
        ]
    }

Installation
------------
KnowIt can be installed as a regular python module by running::

    $ [sudo] pip install knowit

For a better isolation with your system you should use a dedicated virtualenv or install for your user only using
the ``--user`` flag.


External dependencies
-------------------------
This product uses `MediaInfo <http://mediaarea.net/MediaInfo>`_ library, Copyright (c) 2002-2016 `MediaArea.net SARL<mailto:Info@MediaArea.net>`_

Binaries for Windows and MacOS are included. Linux distributions need to manually install MediaInfo.

KnowIt supports MKV regardless if MediaInfo is installed.

MediaInfo increases the number of supported formats and the number of extracted information.
