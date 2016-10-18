# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import logging

import enzyme

from .. import OrderedDict
from ..properties import AudioCodec, Integer, Language, Property, VideoCodec, YesNo
from ..provider import MalformedFileError, Provider
from ..utils import todict


logger = logging.getLogger(__name__)


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
                ('number', Property('number', Integer('video track number'))),
                ('name', Property('name')),
                ('language', Property('language', Language())),
                ('width', Property('width', Integer('width'))),
                ('height', Property('height', Integer('height'))),
                ('scan_type', Property('interlaced', YesNo('Interlaced', 'Progressive'))),
                # ('bit_depth', Property('bit_depth', Integer('video bit depth'))),
                ('codec', Property('codec_id', VideoCodec())),
                ('forced', Property('forced', YesNo(hide_value=False))),
                ('default', Property('default', YesNo(hide_value=False))),
                ('enabled', Property('enabled', YesNo(hide_value=True))),
            ]),
            'audio': OrderedDict([
                ('number', Property('number', Integer('audio track number'))),
                ('name', Property('name')),
                ('language', Property('language', Language())),
                ('codec', Property('codec_id', AudioCodec())),
                ('channels', Property('channels', Integer('audio channels'))),
                ('forced', Property('forced', YesNo(hide_value=False))),
                ('default', Property('default', YesNo(hide_value=False))),
                ('enabled', Property('enabled', YesNo(hide_value=True))),
            ]),
            'subtitle': OrderedDict([
                ('number', Property('number', Integer('subtitle track number'))),
                ('name', Property('name')),
                ('language', Property('language', Language())),
                ('forced', Property('forced', YesNo(hide_value=False))),
                ('default', Property('default', YesNo(hide_value=False))),
                ('enabled', Property('enabled', YesNo(hide_value=True))),
            ]),
        })

    def accepts(self, video_path):
        """Accept only MKV files."""
        return video_path.lower().endswith('.mkv')

    def describe(self, video_path, options):
        """Return video metadata."""
        try:
            with open(video_path, 'rb') as f:
                mkv = enzyme.MKV(f)
        except enzyme.MalformedMKVError:
            logger.warning("Invalid file '%s'", video_path)
            if options['fail_on_error']:
                raise MalformedFileError
            return dict()

        if options['raw']:
            return todict(mkv)

        return self._describe_tracks(mkv.info, mkv.video_tracks, mkv.audio_tracks, mkv.subtitle_tracks)
