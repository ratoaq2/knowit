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
Extract information from a video file:

    $ knowit FooBar.mkv
    For: FooBar.mkv
    KnowIt found: {
        "duration": "0:20:31.071000",
        "video": [
            {
                "number": 1,
                "language": "en",
                "duration": "0:20:31.044000",
                "size": 385321030,
                "width": 1280,
                "height": 720,
                "scan_type": "Progressive",
                "aspect_ratio": "1.778",
                "frame_rate": "23.976",
                "bit_rate": 2503986,
                "bit_depth": 8,
                "codec": "AVC",
                "profile": "High@L4.1",
                "encoder": "x264",
                "media_type": "video/H264"
            }
        ],
        "audio": [
            {
                "number": 2,
                "duration": "0:20:31.076000",
                "size": 59091648,
                "codec": "AC-3",
                "channels": 6,
                "bit_rate": 384000,
                "bit_rate_mode": "CBR",
                "sample_rate": 48000,
                "compression_mode": "Lossy"
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
This product uses `MediaInfo <http://mediaarea.net/MediaInfo>`_ library, Copyright (c) 2002-2016 `MediaArea.net SARL<mailto:Info@MediaArea.net>`_.
Binaries for Windows and MacOS are included. Linux distributions need to manually install MediaInfo.
KnowIt supports MKV regardless if MediaInfo is installed.
MediaInfo increases the number of supported formats and the number of extracted information.
