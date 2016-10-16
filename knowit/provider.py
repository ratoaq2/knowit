# -*- coding: utf-8 -*-
import logging

from six import binary_type, text_type

from . import OrderedDict


logger = logging.getLogger(__name__)

visible_chars_table = dict.fromkeys(range(32))


class Provider(object):
    """Base class for all providers."""

    def __init__(self, mapping):
        """Init method."""
        self.mapping = mapping

    def accepts(self, video_path):
        """Whether or not the video is supported by this provider."""
        raise NotImplementedError

    def describe(self, video_path, options):
        """Read video metadata information."""
        raise NotImplementedError

    def _describe_tracks(self, general_track, video_tracks, audio_tracks, subtitle_tracks):
        props = self._describe_general(general_track)

        video = []
        for track in video_tracks:
            v = self._describe_video_track(track)
            video.append(v)

        audio = []
        for track in audio_tracks:
            v = self._describe_audio_track(track)
            audio.append(v)

        subtitle = []
        for track in subtitle_tracks:
            v = self._describe_subtitle_track(track)
            subtitle.append(v)

        if video:
            props['video'] = video
        if audio:
            props['audio'] = audio
        if subtitle:
            props['subtitle'] = subtitle

        return props

    def _describe_general(self, track):
        """Describe general media info to a dict.

        :param track:
        :return:
        :rtype: dict
        """
        logger.debug('Handling general track')
        return self._describe_track(track, self.mapping['general'])

    def _describe_video_track(self, track):
        """Describe video track to a dict.

        :param track:
        :return:
        :rtype: dict
        """
        logger.debug('Handling video track')
        return self._describe_track(track, self.mapping['video'])

    def _describe_audio_track(self, track):
        """Describe audio track to a dict.

        :param track:
        :return:
        :rtype: dict
        """
        logger.debug('Handling audio track')
        return self._describe_track(track, self.mapping['audio'])

    def _describe_subtitle_track(self, track):
        """Describe subtitle track to a dict.

        :param track:
        :return:
        :rtype: dict
        """
        logger.debug('Handling subtitle track')
        return self._describe_track(track, self.mapping['subtitle'])

    def _describe_track(self, track, mapping):
        """Describe track to a dict.

        :param track:
        :param mapping:
        :type mapping: dict(str, str)
        :return:
        :rtype: dict
        """
        props = OrderedDict()
        for name, prop in mapping.items():
            self._enrich(props, name, track, prop)

        return props

    @staticmethod
    def _enrich(props, name, source, prop):
        if source is not None:
            value = getattr(source, prop.name)
            if value is not None:
                logger.debug('Adding %s with value %r', name, value)
                if isinstance(value, binary_type):
                    value = text_type(value)
                if isinstance(value, text_type):
                    value = value.translate(visible_chars_table)

                props[name] = prop.handler.handle(value, props) if prop.handler is not None else value
