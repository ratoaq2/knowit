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

    $ knowit /folder/Audio Samples/hd_dtsma_7.1.mkv
    For: /folder/Audio Samples/hd_dtsma_7.1.mkv
    Knowit 0.2.0 found:
    {
        "title": "HD DTS-HD Master Audio 7.1",
        "path": "/folder/Audio Samples/hd_dtsma_7.1.mkv",
        "duration": "0:00:21",
        "size": "31.64 MB",
        "bit_rate": "12.0 Mbps",
        "video": [
            {
                "number": 1,
                "duration": "0:00:21",
                "width": "1920 pixel",
                "height": "1080 pixel",
                "scan_type": "Progressive",
                "aspect_ratio": 1.778,
                "pixel_aspect_ratio": 1.0,
                "resolution": "1080p",
                "frame_rate": "29.97 FPS",
                "bit_depth": "8 bit",
                "codec": "H.264",
                "profile": "High",
                "profile_level": "4",
                "encoder": "x264",
                "media_type": "video/H264",
                "default": true,
                "language": "Undetermined"
            }
        ],
        "audio": [
            {
                "number": 2,
                "name": "German",
                "language": "German",
                "duration": "0:00:21",
                "codec": "DTS-HD",
                "profile": [
                    "Master Audio",
                    "Core"
                ],
                "channels_count": [
                    8,
                    6
                ],
                "channels": "7.1",
                "bit_depth": "24 bit",
                "bit_rate": [
                    null,
                    "1.5 Mbps"
                ],
                "bit_rate_mode": [
                    "Variable",
                    "Constant"
                ],
                "sampling_rate": [
                    "96.0 KHz",
                    "48.0 KHz"
                ],
                "compression": [
                    "Lossless",
                    "Lossy"
                ],
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
KnowIt depends on MediaInfo: http://mediaarea.net/MediaInfo

KnowIt supports MKV regardless if MediaInfo is installed.

MediaInfo increases the number of supported formats and the number of extracted information.

Visit their `website <http://mediaarea.net/MediaInfo>`_ and install the proper package for your system.
