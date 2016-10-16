# -*- coding: utf-8 -*-
import logging
import os
import sys

from pymediainfo import MediaInfo

from .. import OrderedDict
from ..properties import AudioCodec, Duration, Language, Property, ScanType, VideoCodec, YesNo
from ..provider import Provider


logger = logging.getLogger(__name__)

MEDIA_INFO_AVAILABLE = False
INITIALIZED = False


def load_native():
    global MEDIA_INFO_AVAILABLE, INITIALIZED
    if INITIALIZED:
        return MEDIA_INFO_AVAILABLE

    os_family = 'windows' if (
        os.name in ('nt', 'dos', 'os2', 'ce')
    ) else (
        'macos' if sys.platform == "darwin" else 'unix'
    )
    logger.debug('Detected os family: %s', os_family)
    try:
        if os_family == 'unix':
            from ctypes import CDLL
            logger.debug('Loading native mediainfo library')
            CDLL('libmediainfo.so.0')
            MEDIA_INFO_AVAILABLE = True
        else:
            os_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../native', os_family))
            if os_family == 'macos':
                from ctypes import CDLL
                logger.debug('Loading native mediainfo library from %s', os_folder)
                CDLL(os.path.join(os_folder, 'libmediainfo.0.dylib'))
                MEDIA_INFO_AVAILABLE = True
            else:
                from ctypes import windll
                is_64bits = sys.maxsize > 2 ** 32
                arch = 'x86_64' if is_64bits else 'i386'
                lib = os.path.join(os_folder, arch)
                logger.debug('Loading native mediainfo library from %s', lib)
                windll.MediaInfo = windll.LoadLibrary(os.path.join(lib, 'MediaInfo.dll'))
                MEDIA_INFO_AVAILABLE = True
        logger.debug('MediaInfo loaded')
    except OSError:
        logger.warning('Unable to load native mediainfo library')
    finally:
        INITIALIZED = True
    return MEDIA_INFO_AVAILABLE


class MediaInfoProvider(Provider):
    """Media Info provider."""

    def __init__(self):
        """Init method."""
        super(MediaInfoProvider, self).__init__({
            'general': OrderedDict([
                ('title', Property('title')),
                ('duration', Property('duration', Duration())),
            ]),
            'video': OrderedDict([
                ('number', Property('track_id')),
                ('name', Property('name')),
                ('language', Property('language', Language())),
                ('duration', Property('duration', Duration())),
                ('size', Property('stream_size')),
                ('width', Property('width')),
                ('height', Property('height')),
                ('scan_type', Property('scan_type', ScanType())),
                ('aspect_ratio', Property('display_aspect_ratio')),
                ('frame_rate', Property('frame_rate')),
                ('bit_rate', Property('bit_rate')),
                ('bit_depth', Property('bit_depth')),
                ('codec', Property('codec', VideoCodec())),
                ('profile', Property('codec_profile')),
                ('encoder', Property('encoded_library_name')),
                ('media_type', Property('internet_media_type')),
                ('forced', Property('forced', YesNo())),
                ('default', Property('default', YesNo())),
                ('enabled', Property('enabled', YesNo())),
            ]),
            'audio': OrderedDict([
                ('number', Property('track_id')),
                ('name', Property('title')),
                ('language', Property('language', Language())),
                ('duration', Property('duration', Duration())),
                ('size', Property('stream_size')),
                ('codec', Property('codec', AudioCodec())),
                ('channels', Property('channel_s')),
                ('bit_rate', Property('bit_rate')),
                ('bit_rate_mode', Property('bit_rate_mode')),
                ('sample_rate', Property('sampling_rate')),
                ('compression_mode', Property('compression_mode')),
                ('forced', Property('forced', YesNo())),
                ('default', Property('default', YesNo())),
                ('enabled', Property('enabled', YesNo())),
            ]),
            'subtitle': OrderedDict([
                ('number', Property('track_id')),
                ('name', Property('title')),
                ('language', Property('language', Language())),
                ('format', Property('format')),
                ('forced', Property('forced', YesNo())),
                ('default', Property('default', YesNo())),
                ('enabled', Property('enabled', YesNo())),
            ]),
        })

    def accepts(self, video_path):
        """Accept any video when MediaInfo is available."""
        return load_native()

    def describe(self, video_path, options):
        """Return video metadata."""
        media = MediaInfo.parse(video_path)
        if options['raw']:
            return media.to_data()

        general_tracks = []
        video_tracks = []
        audio_tracks = []
        subtitle_tracks = []
        for track in media.tracks:
            if track.track_type == 'General':
                general_tracks.append(track)
            elif track.track_type == 'Video':
                video_tracks.append(track)
            elif track.track_type == 'Audio':
                audio_tracks.append(track)
            elif track.track_type == 'Text':
                subtitle_tracks.append(track)

        return self._describe_tracks(general_tracks[0], video_tracks, audio_tracks, subtitle_tracks)
