# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from logging import NullHandler, getLogger

from .. import OrderedDict

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Provider(object):
    """Base class for all providers."""

    def __init__(self, mapping, rules=None):
        """Init method."""
        self.mapping = mapping
        self.rules = rules or {}

    def accepts(self, target):
        """Whether or not the video is supported by this provider."""
        raise NotImplementedError

    def describe(self, target, options):
        """Read video metadata information."""
        raise NotImplementedError

    def _describe_tracks(self, general_track, video_tracks, audio_tracks, subtitle_tracks):
        logger.debug('Handling general track')
        props = self._describe_track(general_track, 'general')

        for track_type, tracks, in (('video', video_tracks),
                                    ('audio', audio_tracks),
                                    ('subtitle', subtitle_tracks)):
            results = []
            for track in tracks:
                logger.debug('Handling %s track', track_type)
                t = self._describe_track(track, track_type)
                if t:
                    results.append(t)

            if results:
                props[track_type] = results

        return props

    def _describe_track(self, track, track_type):
        """Describe track to a dict.

        :param track:
        :param track_type:
        :rtype: dict
        """
        props = OrderedDict()
        context = {}
        for name, prop in self.mapping[track_type].items():
            if not prop:
                # placeholder to be populated by rules. It keeps the order
                props[name] = None
                continue

            value = prop.extract_value(track)
            if value is not None:
                which = context if prop.private else props
                which[name] = value

        for name, rule in self.rules.get(track_type, {}).items():
            if props.get(name) is not None:
                logger.debug('Skipping rule %s since property is already present', name)
                continue

            value = rule.execute(props, context)
            if value is not None:
                props[name] = value
            elif name in props:
                del props[name]

        return props


class ProviderError(Exception):
    """Base class for provider exceptions."""

    pass


class MalformedFileError(ProviderError):
    """Malformed File error."""

    pass


class UnsupportedFileFormatError(ProviderError):
    """Unsupported File Format error."""

    pass
