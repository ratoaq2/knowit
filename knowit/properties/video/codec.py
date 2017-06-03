# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import Property


class VideoCodec(Property):
    """Video Codec handler."""

    video_codecs = {
        # MPEG-1: https://en.wikipedia.org/wiki/MPEG-1
        'MPEG-1V': 'MPEG-1',

        # MPEG-2: https://en.wikipedia.org/wiki/H.262/MPEG-2_Part_2
        'MPEG2': 'MPEG-2',
        'MPEG-2V': 'MPEG-2',

        # Microsoft MPEG-4: https://wiki.multimedia.cx/index.php/Microsoft_MPEG-4
        'MP41': 'Microsoft MPEG-4 v1',
        'MP42': 'Microsoft MPEG-4 v2',
        'MP43': 'Microsoft MPEG-4 v3',
        'DIV3': 'Microsoft MPEG-4',
        'AP41': 'Microsoft MPEG-4',
        'COL1': 'Microsoft MPEG-4',
        'WMV1': 'Microsoft WMV 7',
        'WMV7': 'Microsoft WMV 7',
        'WMV2': 'Microsoft WMV 8',
        'WMV8': 'Microsoft WMV 8',

        # MPEG-4: https://wiki.multimedia.cx/index.php/ISO_MPEG-4 and # https://en.wikipedia.org/wiki/MPEG-4_Part_2
        '3IV2': 'MPEG-4',
        'BLZ0': 'MPEG-4',
        'DIGI': 'MPEG-4',
        'DXGM': 'MPEG-4',
        'EM4A': 'MPEG-4',
        'EPHV': 'MPEG-4',
        'FMP4': 'MPEG-4',
        'FVFW': 'MPEG-4',
        'HDX4': 'MPEG-4',
        'M4CC': 'MPEG-4',
        'M4S2': 'MPEG-4',
        'MP4S': 'MPEG-4',
        'MP4V': 'MPEG-4',
        'MVXM': 'MPEG-4',
        'RMP4': 'MPEG-4',
        'SEDG': 'MPEG-4',
        'SMP4': 'MPEG-4',
        'UMP4': 'MPEG-4',
        'WV1F': 'MPEG-4',
        'MPEG-4V': 'MPEG-4',
        'DIV1': 'DivX',
        'DIVX': 'DivX',
        'DX50': 'DivX',
        'XVID': 'Xvid',
        'XVIX': 'Xvid',
        'ASP': 'DivX',  # V_MPEG-4/ISO/ASP

        # VC-1: https://wiki.multimedia.cx/index.php/VC-1 and https://en.wikipedia.org/wiki/VC-1
        'VC-1': 'VC-1',
        'WMV3': 'VC-1',
        'WMV9': 'VC-1',
        'WMVA': 'VC-1',
        'WVC1': 'VC-1',
        'WMVP': 'VC-1',
        'WVP2': 'VC-1',
        'WMVR': 'VC-1',

        # H.263: https://wiki.multimedia.cx/index.php/H.263
        #        https://en.wikipedia.org/wiki/Sorenson_Media#Sorenson_Spark
        'D263': 'H.263',
        'H263': 'H.263',
        'L263': 'H.263',
        'M263': 'H.263',
        'S263': 'H.263',
        'T263': 'H.263',
        'U263': 'H.263',
        'X263': 'H.263',
        'SORENSON H263': 'H.263',

        # H.264: https://wiki.multimedia.cx/index.php/H.264
        'AVC': 'H.264',
        'AVC1': 'H.264',
        'DAVC': 'H.264',
        'H264': 'H.264',
        'X264': 'H.264',
        'VSSH': 'H.264',

        # H.265
        'HEVC': 'H.265',
        'H265': 'H.265',
        'X265': 'H.265',

        # On2 VP7: https://wiki.multimedia.cx/index.php/On2_VP7
        'VP70': 'On2 VP7',
        'VP71': 'On2 VP7',
        'VP72': 'On2 VP7',

        # On2 VP6: https://wiki.multimedia.cx/index.php/On2_VP6 and https://en.wikipedia.org/wiki/VP6
        'ON2 VP6': 'VP6',
        'VP60': 'On2 VP6',
        'VP61': 'On2 VP6',
        'VP62': 'On2 VP6',

        # VP9: https://en.wikipedia.org/wiki/VP9 and https://wiki.multimedia.cx/index.php/VP9
        'VP9': 'VP9',
        'VP90': 'VP9',

        # Misc
        'JPEG': 'JPEG',
        'QUICKTIME': 'QuickTime',
    }

    def handle(self, value):
        """Handle video codecs values."""
        key = value.upper().split('/')[-1]
        if key.startswith('V_'):
            key = key[2:]

        return self._handle(value, key, self.video_codecs)
