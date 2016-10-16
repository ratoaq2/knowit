# -*- coding: utf-8 -*-

import datetime
import logging

from babelfish import Error as BabelfishError, Language as BabelfishLanguage
from six import text_type

logger = logging.getLogger(__name__)


class Property(object):
    """Property class."""

    def __init__(self, name, handler=None):
        """Init method."""
        self.name = name
        self.handler = handler


class Handler(object):
    """Property Handler abstract class."""

    def handle(self, value, context):
        """How to handle property value."""
        raise NotImplementedError

    @staticmethod
    def _handle(name, value, key, mapping):
        result = mapping.get(key)
        if result is not None:
            return result

        logger.info('Invalid %s: %r', name, value)
        return value


class Duration(Handler):
    """Duration handler."""

    def handle(self, value, context):
        """Return duration as timedelta."""
        if isinstance(value, int):
            return datetime.timedelta(milliseconds=value)
        try:
            return datetime.timedelta(milliseconds=int(float(value)))
        except ValueError:
            pass

        logger.info('Invalid duration: %r', value)
        return value


class ScanType(Handler):
    """Scan Type handler."""

    scan_types = {
        'progressive': 'Progressive',
        'interlaced': 'Interlaced',
        'mbaff': 'Interlaced',
    }

    def handle(self, value, context):
        """Return Progressive or Interlaced."""
        return self._handle('scan type', value, value.lower(), self.scan_types)


class VideoCodec(Handler):
    """Video Codec handler."""

    video_codecs = {
        'AVC': 'h264',
        'HEVC': 'h265',
        'MPEG2': 'Mpeg2',
        'MPEG-1V': 'Mpeg',
        'MP42': 'Mpeg4v2',
        'XviD': 'XviD',
        'DX50': 'DivX',
        'JPEG': 'JPEG',
        'WMV3': 'WMV3',
        'WMV2': 'WMV2',
        'WMV1': 'WMV1',
    }

    def handle(self, value, context):
        """Handle video codecs values."""
        key = value.upper().split('/')[-1]
        if key.startswith('V_'):
            key = key[2:]

        return self._handle('video codec', value, key, self.video_codecs)


class AudioCodec(Handler):
    """Audio codec handler."""

    audio_codecs = {
        'AC3': 'AC3',
        'EAC3': 'EAC3',
        'TRUEHD': 'TrueHD',
        'DTS': 'DTS',
        'AAC': 'AAC',
        'AAC LC': 'AAC',
        'AAC LC-SBR': 'AAC',
        'AAC LC-SBR-PS': 'AAC',
        'DTS-HD': 'DTS',
        'MPA1L2': 'MP2',
        'MPEG/L2': 'MP2',
        'MPA1L3': 'MP3',
        'MPA2L3': 'MP3',
        'MPEG/L3': 'MP3',
        'VORBIS': 'Vorbis',
        # https://wiki.multimedia.cx/index.php?title=Windows_Media_Audio_9
        '160': 'WMA',
        '161': 'WMA',
        '162': 'WMA',
        '163': 'WMA',
    }

    audio_profiles = {
        'DTS-HD': 'HD',
        'AAC LC': 'LC',
        'AAC LC-SBR': 'LC',
        'AAC LC-SBR-PS': 'LC',
    }

    def handle(self, value, context):
        """Handle audio codec and audio profiles."""
        key = text_type(value).upper()
        if key.startswith('A_'):
            key = key[2:]

        profile = self.audio_profiles.get(key)
        if profile:
            context['profile'] = profile

        return self._handle('audio codec', value, key, self.audio_codecs)


class Language(Handler):
    """Language handler."""

    def handle(self, value, context):
        """Handle languages."""
        try:
            if len(value) == 3:
                return BabelfishLanguage.fromalpha3b(value)

            return BabelfishLanguage.fromietf(value)
        except (BabelfishError, ValueError):
            pass

        try:
            return BabelfishLanguage.fromname(value)
        except BabelfishError:
            pass

        logger.info('Invalid language: %r', value)
        return BabelfishLanguage('und')


class YesNo(Handler):
    """Yes or No handler."""

    mapping = {'yes', 'true', '1'}

    def __init__(self, yes=True, no=False):
        """Init method."""
        self.yes = yes
        self.no = no

    def handle(self, value, context):
        """Handle boolean values."""
        v = text_type(value).lower()
        return self.yes if v in self.mapping else self.no
