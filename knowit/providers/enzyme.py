# coding=utf-8
from __future__ import absolute_import

import enzyme

from .. import OrderedDict
from ..provider import Provider

mapping = {
    'general': OrderedDict([
        ('title', 'title'),
        ('duration', 'duration'),
    ]),
    'video': OrderedDict([
        ('number', 'number'),
        ('name', 'name'),
        ('language', 'language'),
        ('codec_id', 'codec'),
        ('width', 'width'),
        ('height', 'height'),
    ]),
    'audio': OrderedDict([
        ('number', 'number'),
        ('name', 'name'),
        ('language', 'language'),
        ('codec_id', 'codec'),
        ('channels', 'channels'),
        ('bit_depth', 'bit_depth'),
    ]),
    'subtitle': OrderedDict(

    ),
}


class EnzymeProvider(Provider):
    """Enzyme Provider."""

    def accepts(self, video_path):
        """Accept only MKV files."""
        return video_path.lower().endswith('.mkv')

    def _getmapping(self, key):
        return mapping[key]

    def describe(self, video_path):
        """Return video metadata."""
        with open(video_path, 'rb') as f:
            mkv = enzyme.MKV(f)

        return self._describe_tracks(mkv.info, mkv.video_tracks, mkv.audio_tracks, mkv.subtitle_tracks)
