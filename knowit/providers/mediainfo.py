# coding=utf-8
import datetime
import os
import sys

from pymediainfo import MediaInfo

from .. import OrderedDict
from ..provider import Provider


MEDIA_INFO_AVAILABLE = False


mapping = {
    'general': OrderedDict([
        ('title', 'title'),
        ('duration', 'duration'),
    ]),
    'video': OrderedDict([
        ('track_id', 'number'),
        ('name', 'name'),
        ('language', 'language'),
        ('duration', 'duration'),
        ('stream_size', 'size'),
        ('width', 'width'),
        ('height', 'height'),
        ('scan_type', 'scan_type'),
        ('display_aspect_ratio', 'aspect_ratio'),
        ('frame_rate', 'frame_rate'),
        ('bit_rate', 'bit_rate'),
        ('bit_depth', 'bit_depth'),
        ('format', 'codec'),
        ('codec_profile', 'profile'),
        ('encoded_library_name', 'encoder'),
        ('internet_media_type', 'media_type'),
    ]),
    'audio': OrderedDict([
        ('track_id', 'number'),
        ('language', 'language'),
        ('duration', 'duration'),
        ('stream_size', 'size'),
        ('format', 'codec'),
        ('channel_s', 'channels'),
        ('bit_rate', 'bit_rate'),
        ('bit_rate_mode', 'bit_rate_mode'),
        ('sampling_rate', 'sample_rate'),
        ('compression_mode', 'compression_mode'),
    ]),
    'subtitle': OrderedDict(

    ),
}

formatting = {
    'duration': lambda d: datetime.timedelta(milliseconds=d)
}


def load_native():
    global MEDIA_INFO_AVAILABLE
    os_family = 'windows' if (
        os.name in ('nt', 'dos', 'os2', 'ce')
    ) else (
        'macos' if sys.platform == "darwin" else 'unix'
    )
    try:
        if os_family == 'unix':
            from ctypes import CDLL
            CDLL('libmediainfo.so.0')
            MEDIA_INFO_AVAILABLE = True
        else:
            os_folder = os.path.join(os.path.dirname(__file__), 'native', os_family)
            if os_family == 'macos':
                from ctypes import CDLL
                CDLL(os.path.join(os_folder, 'libmediainfo.0.dylib'))
                MEDIA_INFO_AVAILABLE = True
            elif os_family == 'windows':
                from ctypes import windll
                is_64bits = sys.maxsize > 2 ** 32
                arch = 'x86_64' if is_64bits else 'i386'
                arch_folder = os_folder if os_family == 'macos' else os.path.join(os_folder, arch)
                lib = os.path.abspath(arch_folder)
                windll.MediaInfo = windll.LoadLibrary(os.path.join(lib, 'MediaInfo.dll'))
                MEDIA_INFO_AVAILABLE = True
    except OSError:
        pass


# Load native media info libraries
load_native()


class MediaInfoProvider(Provider):
    """Media Info provider."""

    def accepts(self, video_path):
        """Accept any video when MediaInfo is available."""
        return MEDIA_INFO_AVAILABLE

    def _getmapping(self, key):
        return mapping[key]

    def _getformatting(self):
        return formatting

    def describe(self, video_path):
        """Return video metadata."""
        media = MediaInfo.parse(video_path)

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
            elif track.track_type == 'Subtitle':
                subtitle_tracks.append(track)

        return self._describe_tracks(general_tracks[0], video_tracks, audio_tracks, subtitle_tracks)
