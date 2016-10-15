# -*- coding: utf-8 -*-
from . import OrderedDict


class Provider(object):
    """Base class for all providers."""

    def accepts(self, video_path):
        """Whether or not the video is supported by this provider."""
        raise NotImplementedError

    def describe(self, video_path):
        """Read video metadata information."""
        raise NotImplementedError

    def _getmapping(self, key):
        raise NotImplementedError

    def _getformatting(self):
        return dict()

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
        return self._describe_track(track, self._getmapping('general'))

    def _describe_video_track(self, track):
        """Describe video track to a dict.

        :param track:
        :return:
        :rtype: dict
        """
        return self._describe_track(track, self._getmapping('video'))

    def _describe_audio_track(self, track):
        """Describe audio track to a dict.

        :param track:
        :return:
        :rtype: dict
        """
        return self._describe_track(track, self._getmapping('audio'))

    def _describe_subtitle_track(self, track):
        """Describe subtitle track to a dict.

        :param track:
        :return:
        :rtype: dict
        """
        return self._describe_track(track, self._getmapping('subtitle'))

    def _describe_track(self, track, mapping):
        """Describe track to a dict.

        :param track:
        :param mapping:
        :type mapping: dict(str, str)
        :return:
        :rtype: dict
        """
        props = OrderedDict()
        f = self._getformatting()
        for k, v in mapping.items():
            self._enrich(track, k, props, v, f.get(k))

        return props

    @staticmethod
    def _enrich(source, source_key, target, target_key=None, value_formatter=None):
        if source is not None:
            value = getattr(source, source_key) if not callable(target_key) else target_key(source)
            if value is not None:
                target[target_key or source_key] = (
                    value_formatter(value) if value_formatter is not None else value)
