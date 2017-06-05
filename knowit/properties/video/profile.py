# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import Configurable


class VideoProfile(Configurable):
    """Video Profile property."""

    @classmethod
    def _extract_key(cls, value):
        return value.upper().split('@')[0]


class VideoProfileLevel(Configurable):
    """Video Profile Level property."""

    @classmethod
    def _extract_key(cls, value):
        values = value.upper().split('@')
        if len(values) > 1:
            return values[1]

        # There's no level, so don't warn or report it
        return False


class VideoProfileTier(Configurable):
    """Video Profile Tier property."""

    @classmethod
    def _extract_key(cls, value):
        values = value.upper().split('@')
        if len(values) > 2:
            return values[2]

        # There's no tier, so don't warn or report it
        return False
