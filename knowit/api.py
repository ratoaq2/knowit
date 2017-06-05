# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import OrderedDict
from .config import Config
from .providers import (
    EnzymeProvider,
    MediaInfoProvider,
)

available_providers = OrderedDict([])


def know(video_path, context=None):
    """Return a dict containing the video metadata.

    :param video_path:
    :type video_path: string
    :param context:
    :type context: dict
    :return:
    :rtype: dict
    """
    context = context or {}
    context.setdefault('profile', 'default')
    if not available_providers:
        config = Config.build(context.get('config'))
        lib_location = context.get('lib_location') or config.general.get('lib_location')
        available_providers['mediainfo'] = MediaInfoProvider(config, lib_location)
        available_providers['enzyme'] = EnzymeProvider(config)

    for name, provider in available_providers.items():
        if name != (context.get('provider') or name):
            continue

        if provider.accepts(video_path):
            return provider.describe(video_path, context)

    return {}
