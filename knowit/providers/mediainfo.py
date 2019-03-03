# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
from logging import DEBUG, NullHandler, getLogger
from subprocess import check_output, CalledProcessError
from xml.dom import minidom
from xml.etree import ElementTree

from pymediainfo import MediaInfo
from pymediainfo import __version__ as pymediainfo_version

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
    Quantity,
    ScanType,
    SubtitleFormat,
    VideoCodec,
    VideoEncoder,
    VideoProfile,
    VideoProfileLevel,
    VideoProfileTier,
    YesNo,
)
from ..property import (
    MultiValue,
    Property,
)
from ..provider import (
    MalformedFileError,
    Provider,
)
from ..rules import (
    AtmosRule,
    AudioChannelsRule,
    ClosedCaptionRule,
    DtsHdRule,
    HearingImpairedRule,
    LanguageRule,
    ResolutionRule,
)
from ..units import units
from ..utils import (
    define_candidate,
    detect_os,
)

logger = getLogger(__name__)
logger.addHandler(NullHandler())


WARN_MSG = r'''
=========================================================================================
MediaInfo not found on your system or could not be loaded.
Visit https://mediaarea.net/ to download it.
If you still have problems, please check if the downloaded version matches your system.
To load MediaInfo from a specific location, please define the location as follow:
  knowit --mediainfo /usr/local/mediainfo/lib <video_path>
  knowit --mediainfo /usr/local/mediainfo/bin <video_path>
  knowit --mediainfo "C:\Program Files\MediaInfo" <video_path>
  knowit --mediainfo C:\Software\MediaInfo.dll <video_path>
  knowit --mediainfo C:\Software\MediaInfo.exe <video_path>
  knowit --mediainfo /opt/mediainfo/libmediainfo.so <video_path>
  knowit --mediainfo /opt/mediainfo/libmediainfo.dylib <video_path>
=========================================================================================
'''


class MediaInfoExecutor(object):
    """Media info executable knows how to execute media info: using ctypes or cli."""

    locations = {
        'unix': ('/usr/local/mediainfo/lib', '/usr/local/mediainfo/bin', '__PATH__'),
        'windows': ('__PATH__', ),
        'macos': ('__PATH__', ),
    }

    def __init__(self, location):
        """Constructor."""
        self.location = location

    def extract_info(self, filename):
        """Extract media info."""
        return self._execute(filename)

    def _execute(self, filename):
        raise NotImplementedError

    @classmethod
    def get_executor_instance(cls, suggested_path=None):
        """Return the executor instance."""
        os_family = detect_os()
        logger.debug('Detected os: %s', os_family)
        for exec_cls in (MediaInfoCTypesExecutor, MediaInfoCliExecutor):
            executor = exec_cls.create(os_family, suggested_path)
            if executor:
                return executor


class MediaInfoCliExecutor(MediaInfoExecutor):
    """Media info using cli."""

    version_re = re.compile(r'\bv(?P<major>\d+)\.(?P<minor>\d+)\b')

    names = {
        'unix': ('mediainfo', ),
        'windows': ('MediaInfo.exe', ),
        'macos': ('mediainfo', ),
    }

    def __init__(self, location, version):
        """Constructor."""
        super(MediaInfoCliExecutor, self).__init__(location)
        self.version = version

    def _execute(self, filename):
        output_type = 'OLDXML' if self.version >= (17, 10) else 'XML'

        return MediaInfo(check_output([self.location, '--Output=' + output_type, '--Full', filename]))

    @classmethod
    def _get_version(cls, output):
        match = cls.version_re.search(output)
        if match:
            match_dict = match.groupdict()
            return int(match_dict['major']), int(match_dict['minor'])

    @classmethod
    def create(cls, os_family=None, suggested_path=None):
        """Create the executor instance."""
        for candidate in define_candidate(cls.locations, cls.names, os_family, suggested_path):
            try:
                output = check_output([candidate, '--version'])
                version = cls._get_version(output)
                if version:
                    logger.debug('MediaInfo cli detected: %s', candidate)
                    return MediaInfoCliExecutor(candidate, version)
            except CalledProcessError as e:
                # old mediainfo returns non-zero for mediainfo --version
                version = cls._get_version(e.output)
                if version:
                    logger.debug('MediaInfo cli detected: %s', candidate)
                    return MediaInfoCliExecutor(candidate, version)
            except OSError:
                pass


class MediaInfoCTypesExecutor(MediaInfoExecutor):
    """Media info ctypes."""

    names = {
        'unix': ('libmediainfo.so.0', ),
        'windows': ('MediaInfo.dll', ),
        'macos': ('libmediainfo.0.dylib', 'libmediainfo.dylib'),
    }

    def __init__(self, location):
        """Constructor."""
        super(MediaInfoCTypesExecutor, self).__init__(location)

    def _execute(self, filename):
        # Create a MediaInfo handle
        return MediaInfo.parse(filename, library_file=self.location)

    @classmethod
    def create(cls, os_family=None, suggested_path=None):
        """Create the executor instance."""
        for candidate in define_candidate(cls.locations, cls.names, os_family, suggested_path):
            if MediaInfo.can_parse(candidate):
                logger.debug('MediaInfo library detected: %s', candidate)
                return MediaInfoCTypesExecutor(candidate)


class MediaInfoProvider(Provider):
    """Media Info provider."""

    executor = None

    def __init__(self, config, suggested_path):
        """Init method."""
        super(MediaInfoProvider, self).__init__(config, {
            'general': OrderedDict([
                ('title', Property('title', description='media title')),
                ('path', Property('complete_name', description='media path')),
                ('duration', Duration('duration', description='media duration')),
                ('size', Quantity('file_size', units.byte, description='media size')),
                ('bit_rate', Quantity('overall_bit_rate', units.bps, description='media bit rate')),
            ]),
            'video': OrderedDict([
                ('id', Basic('track_id', int, allow_fallback=True, description='video track number')),
                ('name', Property('name', description='video track name')),
                ('language', Language('language', description='video language')),
                ('duration', Duration('duration', description='video duration')),
                ('size', Quantity('stream_size', units.byte, description='video stream size')),
                ('width', Quantity('width', units.pixel)),
                ('height', Quantity('height', units.pixel)),
                ('scan_type', ScanType(config, 'scan_type', default='Progressive', description='video scan type')),
                ('aspect_ratio', Basic('display_aspect_ratio', float, description='display aspect ratio')),
                ('pixel_aspect_ratio', Basic('pixel_aspect_ratio', float, description='pixel aspect ratio')),
                ('resolution', None),  # populated with ResolutionRule
                ('frame_rate', Quantity('frame_rate', units.FPS, float, description='video frame rate')),
                # frame_rate_mode
                ('bit_rate', Quantity('bit_rate', units.bps, description='video bit rate')),
                ('bit_depth', Quantity('bit_depth', units.bit, description='video bit depth')),
                ('codec', VideoCodec(config, 'codec', description='video codec')),
                ('profile', VideoProfile(config, 'codec_profile', description='video codec profile')),
                ('profile_level', VideoProfileLevel(config, 'codec_profile', description='video codec profile level')),
                ('profile_tier', VideoProfileTier(config, 'codec_profile', description='video codec profile tier')),
                ('encoder', VideoEncoder(config, 'encoded_library_name', description='video encoder')),
                ('media_type', Property('internet_media_type', description='video media type')),
                ('forced', YesNo('forced', hide_value=False, description='video track forced')),
                ('default', YesNo('default', hide_value=False, description='video track default')),
            ]),
            'audio': OrderedDict([
                ('id', Basic('track_id', int, allow_fallback=True, description='audio track number')),
                ('name', Property('title', description='audio track name')),
                ('language', Language('language', description='audio language')),
                ('duration', Duration('duration', description='audio duration')),
                ('size', Quantity('stream_size', units.byte, description='audio stream size')),
                ('codec', MultiValue(AudioCodec(config, 'codec', description='audio codec'))),
                ('profile', MultiValue(AudioProfile(config, 'format_profile', description='audio codec profile'),
                                       delimiter=' / ')),
                ('channels_count', MultiValue(AudioChannels('channel_s', description='audio channels count'))),
                ('channel_positions', MultiValue(name='other_channel_positions', handler=(lambda x, *args: x),
                                                 delimiter=' / ', private=True, description='audio channels position')),
                ('channels', None),  # populated with AudioChannelsRule
                ('bit_depth', Quantity('bit_depth', units.bit, description='audio bit depth')),
                ('bit_rate', MultiValue(Quantity('bit_rate', units.bps, description='audio bit rate'))),
                ('bit_rate_mode', MultiValue(BitRateMode(config, 'bit_rate_mode', description='audio bit rate mode'))),
                ('sampling_rate', MultiValue(Quantity('sampling_rate', units.Hz, description='audio sampling rate'))),
                ('compression', MultiValue(AudioCompression(config, 'compression_mode',
                                                            description='audio compression'))),
                ('forced', YesNo('forced', hide_value=False, description='audio track forced')),
                ('default', YesNo('default', hide_value=False, description='audio track default')),
            ]),
            'subtitle': OrderedDict([
                ('id', Basic('track_id', int, allow_fallback=True, description='subtitle track number')),
                ('name', Property('title', description='subtitle track name')),
                ('language', Language('language', description='subtitle language')),
                ('hearing_impaired', None),  # populated with HearingImpairedRule
                ('_closed_caption', Property('captionservicename', private=True)),
                ('closed_caption', None),  # populated with ClosedCaptionRule
                ('format', SubtitleFormat(config, 'codec_id', description='subtitle format')),
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
                ('_atmosrule', AtmosRule('atmos rule')),
                ('_dtshdrule', DtsHdRule('dts-hd rule')),
            ]),
            'subtitle': OrderedDict([
                ('language', LanguageRule('subtitle language')),
                ('hearing_impaired', HearingImpairedRule('subtitle hearing impaired')),
                ('closed_caption', ClosedCaptionRule('closed caption')),
            ])
        })
        self.executor = MediaInfoExecutor.get_executor_instance(suggested_path)

    def accepts(self, video_path):
        """Accept any video when MediaInfo is available."""
        if self.executor is None:
            logger.warning(WARN_MSG)
            self.executor = False

        return self.executor and video_path.lower().endswith(VIDEO_EXTENSIONS)

    def describe(self, video_path, context):
        """Return video metadata."""
        media_info = self.executor.extract_info(video_path)
        if logger.isEnabledFor(DEBUG):
            xml = ElementTree.tostring(media_info.xml_dom).replace('\r', '').replace('\n', '')
            logger.debug('Video %r scanned using mediainfo %r has raw data:\n%s',
                         video_path, self.executor.location,
                         minidom.parseString(xml).toprettyxml(indent='  ', newl='\n', encoding='utf-8'))

        data = media_info.to_data()
        result = {}
        if data.get('tracks'):
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

            result = self._describe_tracks(video_path, general_tracks[0] if general_tracks else {},
                                           video_tracks, audio_tracks, subtitle_tracks, context)
        if not result:
            logger.warning('Invalid file %r', video_path)
            if context.get('fail_on_error', True):
                raise MalformedFileError

        result['provider'] = self.executor.location
        return result

    @property
    def version(self):
        """Return mediainfo version information."""
        return pymediainfo_version, self.executor.location if self.executor else None
