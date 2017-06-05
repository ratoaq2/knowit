# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import Configurable


class SubtitleEncoding(Configurable):
    """Subtitle Encoding handler."""

    @classmethod
    def _extract_key(cls, value):
        key = value.upper()
        if key.startswith('S_'):
            key = key[2:]

        return key.split('/')[-1]
