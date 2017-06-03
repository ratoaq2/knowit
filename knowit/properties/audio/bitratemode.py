# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ..property import Property


class BitRateMode(Property):
    """Bit Rate mode property."""

    mapping = {
        'VBR': 'Variable',
        'CBR': 'Constant',
    }

    def handle(self, value):
        """Return Variable or Constant."""
        return self._handle(value, value.upper(), self.mapping)
