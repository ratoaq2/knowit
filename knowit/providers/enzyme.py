# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import os

from collections import defaultdict
from logging import NullHandler, getLogger
import enzyme

from .. import OrderedDict
from ..properties import (
    AudioCodec,
    Basic,
    Duration,
    Language,
    Property,
    Quantity,
    VideoCodec,
    YesNo,
)
from ..providers.provider import (
    MalformedFileError,
    Provider,
)
from ..rules import (
    AudioChannelsRule,
    HearingImpairedRule,
    LanguageRule,
    ResolutionRule,
)
from ..units import units
from ..utils import todict

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class EnzymeProvider(Provider):
    """Enzyme Provider."""

    def __init__(self):
        """Init method."""
        super(EnzymeProvider, self).__init__({
            'general': OrderedDict([
                ('title', Property('title', description='media title')),
                ('path', Property('complete_name', description='media path')),
                ('size', Quantity('file_size', units.byte, description='media size')),
                ('duration', Duration('duration', description='media duration')),
            ]),
            'video': OrderedDict([
                ('number', Basic('number', int, description='video track number')),
                ('name', Property('name', description='video track name')),
                ('language', Language('language', description='video language')),
                ('width', Quantity('width', units.pixel)),
                ('height', Quantity('height', units.pixel)),
                ('scan_type', YesNo('interlaced', yes='Interlaced', no='Progressive', default='Progressive',
                                    description='video scan type')),
                ('resolution', None),  # populated with ResolutionRule
                # ('bit_depth', Property('bit_depth', Integer('video bit depth'))),
                ('codec', VideoCodec('codec_id', description='video codec')),
                ('forced', YesNo('forced', hide_value=False, description='video track forced')),
                ('default', YesNo('default', hide_value=False, description='video track default')),
                ('enabled', YesNo('enabled', hide_value=True, description='video track enabled')),
            ]),
            'audio': OrderedDict([
                ('number', Basic('number', int, description='audio track number')),
                ('name', Property('name', description='audio track name')),
                ('language', Language('language', description='audio language')),
                ('codec', AudioCodec('codec_id', description='audio codec')),
                ('channels_count', Basic('channels', int, description='audio channels count')),
                ('channels', None),  # populated with AudioChannelsRule
                ('forced', YesNo('forced', hide_value=False, description='audio track forced')),
                ('default', YesNo('default', hide_value=False, description='audio track default')),
                ('enabled', YesNo('enabled', hide_value=True, description='audio track enabled')),
            ]),
            'subtitle': OrderedDict([
                ('number', Basic('number', int, description='subtitle track number')),
                ('name', Property('name', description='subtitle track name')),
                ('language', Language('language', description='subtitle language')),
                ('hearing_impaired', None),  # populated with HearingImpairedRule
                ('forced', YesNo('forced', hide_value=False, description='subtitle track forced')),
                ('default', YesNo('default', hide_value=False, description='subtitle track default')),
                ('enabled', YesNo('enabled', hide_value=True, description='subtitle track enabled')),
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

    def accepts(self, video_path):
        """Accept only MKV files."""
        return video_path.lower().endswith('.mkv')

    def describe(self, video_path, options):
        """Return video metadata."""
        try:
            with open(video_path, 'rb') as f:
                data = defaultdict(dict)
                ff = todict(enzyme.MKV(f))
                data.update(ff)
                data['info']['complete_name'] = video_path
                data['info']['file_size'] = os.path.getsize(video_path)

        except enzyme.MalformedMKVError:  # pragma: no cover
            logger.warning("Invalid file '%s'", video_path)
            if options.get('fail_on_error'):
                raise MalformedFileError
            return {}

        if options.get('raw'):
            return data

        return self._describe_tracks(data.get('info'), data.get('video_tracks', []),
                                     data.get('audio_tracks', []), data.get('subtitle_tracks', []))
