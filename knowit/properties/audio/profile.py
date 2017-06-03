# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from six import text_type

from ..property import Property


class AudioProfile(Property):
    """Audio profile property."""

    audio_profiles = {
        'AAC MAIN': 'Main',
        'AAC LC': 'Low Complexity',
        'AAC LC-SBR': 'Low Complexity',
        'AAC LC-SBR-PS': 'Low Complexity',
    }

    def handle(self, value):
        """Handle profiles."""
        key = text_type(value).upper()
        return self.audio_profiles.get(key)
