# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..property import Property


class AudioCompression(Property):
    """Audio Compression property."""

    mapping = {
        'lossy': 'Lossy',
        'lossless': 'Lossless',
    }

    def handle(self, value):
        """Return Lossy or Lossless."""
        return self._handle(value, value.lower(), self.mapping)
