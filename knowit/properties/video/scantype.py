# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import Property


class ScanType(Property):
    """Scan Type property."""

    scan_types = {
        'progressive': 'Progressive',
        'interlaced': 'Interlaced',
        'mbaff': 'Interlaced',
    }

    def handle(self, value):
        """Return Progressive or Interlaced."""
        return self._handle(value, value.lower(), self.scan_types)
