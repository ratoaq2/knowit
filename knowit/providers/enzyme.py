# -*- coding: utf-8 -*-
from __future__ import absolute_import

import enzyme

from .. import OrderedDict
from ..properties import AudioCodec, Language, Property, VideoCodec, YesNo
from ..provider import Provider
from ..utils import todict


class EnzymeProvider(Provider):
    """Enzyme Provider."""

    def __init__(self):
        """Init method."""
        super(EnzymeProvider, self).__init__({
            'general': OrderedDict([
                ('title', Property('title')),
                ('duration', Property('duration')),
            ]),
            'video': OrderedDict([
                ('number', Property('number')),
                ('name', Property('name')),
                ('language', Property('language', Language())),
                ('width', Property('width')),
                ('height', Property('height')),
                ('scan_type', Property('interlaced', YesNo('Interlaced', 'Progressive'))),
                ('codec', Property('codec_id', VideoCodec())),
                ('forced', Property('forced', YesNo())),
                ('default', Property('default', YesNo())),
                ('enabled', Property('enabled', YesNo())),
            ]),
            'audio': OrderedDict([
                ('number', Property('number')),
                ('name', Property('name')),
                ('language', Property('language', Language())),
                ('codec', Property('codec_id', AudioCodec())),
                ('channels', Property('channels')),
                ('bit_depth', Property('bit_depth')),
                ('forced', Property('forced', YesNo())),
                ('default', Property('default', YesNo())),
                ('enabled', Property('enabled', YesNo())),
            ]),
            'subtitle': OrderedDict([
                ('number', Property('number')),
                ('name', Property('name')),
                ('language', Property('language', Language())),
                ('forced', Property('forced', YesNo())),
                ('default', Property('default', YesNo())),
                ('enabled', Property('enabled', YesNo())),
            ]),
        })

    def accepts(self, video_path):
        """Accept only MKV files."""
        return video_path.lower().endswith('.mkv')

    def describe(self, video_path, options):
        """Return video metadata."""
        with open(video_path, 'rb') as f:
            mkv = enzyme.MKV(f)

        if options['raw']:
            return todict(mkv)

        return self._describe_tracks(mkv.info, mkv.video_tracks, mkv.audio_tracks, mkv.subtitle_tracks)
