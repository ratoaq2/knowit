# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import Property


class SubtitleFormat(Property):
    """Subtitle Format property."""

    formats = {
        # Presentation Graphic Stream
        'S_HDMV/PGS': 'Presentation Graphic Stream',
        '144': 'Presentation Graphic Stream',

        # VobSub
        'S_VOBSUB': 'VobSub',
        'E0': 'VobSub',

        # SubRip
        'S_TEXT/UTF8': 'SubRip',

        # https://en.wikipedia.org/wiki/SubStation_Alpha
        'S_TEXT/SSA': 'SubStation Alpha',
        'S_TEXT/ASS': 'Advanced SubStation Alpha',

        # https://en.wikipedia.org/wiki/MPEG-4_Part_17
        'TX3G': 'MPEG-4 Timed Text',
    }

    def handle(self, value):
        """Handle subtitle format values."""
        key = value.upper()
        return self._handle(value, key, self.formats)
