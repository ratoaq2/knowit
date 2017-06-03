# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import Property


class SubtitleEncoding(Property):
    """Subtitle Encoding handler."""

    encoding = {
        'S_TEXT/UTF8': 'UTF-8'
    }

    def handle(self, value):
        """Handle subtitle encoding values."""
        key = value.upper()
        return self.encoding.get(key)
