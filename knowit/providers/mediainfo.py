# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import locale
import os
import sys

from ctypes import c_size_t, c_void_p, c_wchar_p
from logging import NullHandler, getLogger
from pymediainfo import MediaInfo

from .provider import (
    MalformedFileError,
    Provider,
)
from .. import (
    OrderedDict,
    VIDEO_EXTENSIONS,
)
from ..properties import (
    AudioChannels,
    AudioCodec,
    AudioCompression,
    AudioProfile,
    Basic,
    BitRateMode,
    Duration,
    Language,
    MultiValue,
    Property,
    Quantity,
    ScanType,
    SubtitleEncoding,
    SubtitleFormat,
    VideoCodec,
    YesNo,
)
from ..rules import (
    AudioChannelsRule,
    HearingImpairedRule,
    LanguageRule,
    ResolutionRule,
)
from ..units import units

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class MediaInfoProvider(Provider):
    """Media Info provider."""

    def __init__(self):
        """Init method."""
        super(MediaInfoProvider, self).__init__({
            'general': OrderedDict([
                ('title', Property('title', description='media title')),
                ('path', Property('complete_name', description='media path')),
                ('duration', Duration('duration', description='media duration')),
                ('size', Quantity('file_size', units.byte, description='media size')),
                ('bit_rate', Quantity('overall_bit_rate', units.bps, description='media bit rate')),
            ]),
            'video': OrderedDict([
                ('number', Basic('track_id', int, description='video track number')),
                ('name', Property('name', description='video track name')),
                ('language', Language('language', description='video language')),
                ('duration', Duration('duration', description='video duration')),
                ('size', Quantity('stream_size', units.byte, description='video stream size')),
                ('width', Quantity('width', units.pixel)),
                ('height', Quantity('height', units.pixel)),
                ('scan_type', ScanType('scan_type', default='Progressive', description='video scan type')),
                ('aspect_ratio', Basic('display_aspect_ratio', float, description='display aspect ratio')),
                ('pixel_aspect_ratio', Basic('pixel_aspect_ratio', float, description='pixel aspect ratio')),
                ('resolution', None),  # populated with ResolutionRule
                ('frame_rate', Quantity('frame_rate', units.FPS, float, description='video frame rate')),
                # frame_rate_mode
                ('bit_rate', Quantity('bit_rate', units.bps, description='video bit rate')),
                ('bit_depth', Quantity('bit_depth', units.bit, description='video bit depth')),
                ('codec', VideoCodec('codec', description='video codec')),
                ('profile', Property('codec_profile', description='video codec profile')),
                ('encoder', Property('encoded_library_name', description='video encoder')),
                ('media_type', Property('internet_media_type', description='video media type')),
                ('forced', YesNo('forced', hide_value=False, description='video track forced')),
                ('default', YesNo('default', hide_value=False, description='video track default')),
            ]),
            'audio': OrderedDict([
                ('number', Basic('track_id', int, description='audio track number')),
                ('name', Property('title', description='audio track name')),
                ('language', Language('language', description='audio language')),
                ('duration', Duration('duration', description='audio duration')),
                ('size', Quantity('stream_size', units.byte, description='audio stream size')),
                ('codec', MultiValue(AudioCodec('codec', description='audio codec'))),
                ('profile', MultiValue(AudioProfile('codec', description='audio codec profile'))),
                ('channels_count', MultiValue(AudioChannels('channel_s', description='audio channels count'))),
                ('channel_positions', MultiValue(name='other_channel_positions', handler=(lambda x, *args: x),
                                                 delimiter=' / ', private=True, description='audio channels position')),
                ('channels', None),  # populated with AudioChannelsRule
                ('bit_depth', Quantity('bit_depth', units.bit, description='audio bit depth')),
                ('bit_rate', MultiValue(Quantity('bit_rate', units.bps, description='audio bit rate'))),
                ('bit_rate_mode', MultiValue(BitRateMode('bit_rate_mode', description='audio bit rate mode'))),
                ('sampling_rate', MultiValue(Quantity('sampling_rate', units.Hz, description='audio sampling rate'))),
                ('compression', MultiValue(AudioCompression('compression_mode', description='audio compression'))),
                ('forced', YesNo('forced', hide_value=False, description='audio track forced')),
                ('default', YesNo('default', hide_value=False, description='audio track default')),
            ]),
            'subtitle': OrderedDict([
                ('number', Basic('track_id', int, description='subtitle track number')),
                ('name', Property('title', description='subtitle track name')),
                ('language', Language('language', description='subtitle language')),
                ('hearing_impaired', None),  # populated with HearingImpairedRule
                ('format', SubtitleFormat('codec_id', description='subtitle format')),
                ('encoding', SubtitleEncoding('codec_id', description='subtitle encoding')),
                ('forced', YesNo('forced', hide_value=False, description='subtitle track forced')),
                ('default', YesNo('default', hide_value=False, description='subtitle track default')),
            ]),
        }, {
            'video': OrderedDict([
                ('language', LanguageRule('video language')),
                ('resolution', ResolutionRule('video resolution')),
            ]),
            'audio': OrderedDict([
                ('language', LanguageRule('audio language')),
                ('channels', AudioChannelsRule('audio channels')),
            ]),
            'subtitle': OrderedDict([
                ('language', LanguageRule('subtitle language')),
                ('hearing_impaired', HearingImpairedRule('subtitle hearing impaired')),
            ])
        })
        self.native_lib = self._create_native_lib()

    @staticmethod
    def _create_native_lib():
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
                so_name = 'libmediainfo.so.0'
                for location in ('/usr/local/mediainfo/lib',):
                    candidate = os.path.join(location, so_name)
                    if os.path.isfile(candidate):
                        so_name = candidate
                        break
                lib = CDLL(so_name)
            else:  # pragma: no cover
                os_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../native', os_family))
                if os_family == 'macos':
                    from ctypes import CDLL
                    logger.debug('Loading native mediainfo library from %s', os_folder)
                    lib = CDLL(os.path.join(os_folder, 'libmediainfo.0.dylib'))
                else:
                    from ctypes import windll
                    is_64bits = sys.maxsize > 2 ** 32
                    arch = 'x86_64' if is_64bits else 'i386'
                    lib = os.path.join(os_folder, arch)
                    logger.debug('Loading native mediainfo library from %s', lib)
                    dll_filename = os.path.join(lib, 'MediaInfo.dll')
                    if sys.version_info[:3] == (2, 7, 13):
                        # http://bugs.python.org/issue29082
                        dll_filename = str(dll_filename)
                    lib = windll.MediaInfo = windll.LoadLibrary(dll_filename)

            lib.MediaInfo_Inform.restype = c_wchar_p
            lib.MediaInfo_New.argtypes = []
            lib.MediaInfo_New.restype = c_void_p
            lib.MediaInfo_Option.argtypes = [c_void_p, c_wchar_p, c_wchar_p]
            lib.MediaInfo_Option.restype = c_wchar_p
            lib.MediaInfo_Inform.argtypes = [c_void_p, c_size_t]
            lib.MediaInfo_Inform.restype = c_wchar_p
            lib.MediaInfo_Open.argtypes = [c_void_p, c_wchar_p]
            lib.MediaInfo_Open.restype = c_size_t
            lib.MediaInfo_Delete.argtypes = [c_void_p]
            lib.MediaInfo_Delete.restype = None
            lib.MediaInfo_Close.argtypes = [c_void_p]
            lib.MediaInfo_Close.restype = None
            logger.debug('MediaInfo loaded')
            return lib
        except OSError:
            logger.warning('Unable to load native mediainfo library')

    def _parse(self, filename):
        lib = self.native_lib
        # Create a MediaInfo handle
        handle = lib.MediaInfo_New()
        lib.MediaInfo_Option(handle, 'CharSet', 'UTF-8')
        # Fix for https://github.com/sbraz/pymediainfo/issues/22
        # Python 2 does not change LC_CTYPE
        # at startup: https://bugs.python.org/issue6203
        if sys.version_info < (3, ) and os.name == 'posix' and locale.getlocale() == (None, None):
            locale.setlocale(locale.LC_CTYPE, locale.getdefaultlocale())
        lib.MediaInfo_Option(None, 'Inform', 'XML')
        lib.MediaInfo_Option(None, 'Complete', '1')
        lib.MediaInfo_Open(handle, filename)
        xml = lib.MediaInfo_Inform(handle, 0)
        # Delete the handle
        lib.MediaInfo_Close(handle)
        lib.MediaInfo_Delete(handle)
        return MediaInfo(xml)

    def accepts(self, video_path):
        """Accept any video when MediaInfo is available."""
        return self.native_lib and video_path.lower().endswith(VIDEO_EXTENSIONS)

    def describe(self, video_path, options):
        """Return video metadata."""
        data = self._parse(video_path).to_data()
        if options.get('raw'):
            return data

        general_tracks = []
        video_tracks = []
        audio_tracks = []
        subtitle_tracks = []
        for track in data.get('tracks'):
            track_type = track.get('track_type')
            if track_type == 'General':
                general_tracks.append(track)
            elif track_type == 'Video':
                video_tracks.append(track)
            elif track_type == 'Audio':
                audio_tracks.append(track)
            elif track_type == 'Text':
                subtitle_tracks.append(track)

        result = self._describe_tracks(general_tracks[0] if general_tracks else None,
                                       video_tracks, audio_tracks, subtitle_tracks)
        if not result:
            logger.warning("Invalid file '%s'", video_path)
            if options.get('fail_on_error'):
                raise MalformedFileError

        return result
