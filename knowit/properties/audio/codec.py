# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import text_type

from ..property import Property


class AudioCodec(Property):
    """Audio codec property."""

    audio_codecs = {
        # Dolby Digital
        'AC3': 'Dolby Digital',
        'AC3/BSID9': 'Dolby Digital',
        'AC3/BSID10': 'Dolby Digital',
        'BSID9': 'Dolby Digital',
        'BSID10': 'Dolby Digital',
        '2000': 'Dolby Digital',

        # Dolby Digital Plus
        'EAC3': 'Dolby Digital Plus',
        'AC3+': 'Dolby Digital Plus',

        # Dolby TrueHD
        'TRUEHD': 'Dolby TrueHD',

        # Dolby Atmos
        'ATMOS': 'Dolby Atmos',

        # DTS
        'DTS': 'DTS',

        # DTS-HD Master Audio
        'DTS-HD': 'DTS-HD Master Audio',

        # AAC
        'AAC': 'AAC',
        'AAC MAIN': 'AAC',
        'AAC LC': 'AAC',
        'AAC LC-SBR': 'AAC',
        'AAC LC-SBR-PS': 'AAC',

        # FLAC
        'FLAC': 'FLAC',

        # PCM
        'PCM': 'PCM',

        # https://en.wikipedia.org/wiki/MPEG-1_Audio_Layer_II
        'MPA1L2': 'MP2',
        'MPEG/L2': 'MP2',

        # https://en.wikipedia.org/wiki/MP3
        'MPA1L3': 'MP3',
        'MPA2L3': 'MP3',
        'MPEG/L3': 'MP3',
        '50': 'MP3',
        '55': 'MP3',

        # Vorbis
        'VORBIS': 'Vorbis',

        # Opus
        'OPUS': 'Opus',

        # https://wiki.multimedia.cx/index.php?title=Windows_Media_Audio_9
        '160': 'WMA 1',
        '161': 'WMA 2',
        '162': 'WMA Pro',
    }

    def handle(self, value):
        """Handle audio codec."""
        key = text_type(value).upper()
        if key.startswith('A_'):
            key = key[2:]

        return self._handle(value, key, self.audio_codecs)
