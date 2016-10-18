# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import OrderedDict
from .providers.enzyme import EnzymeProvider
from .providers.mediainfo import MediaInfoProvider


available_providers = OrderedDict([
    ('mediainfo', MediaInfoProvider()),
    ('enzyme', EnzymeProvider()),
])


def knowit(video_path, options):
    """Return a dict containing the video metadata.

    :param video_path:
    :type video_path: string
    :param options:
    :type options: dict
    :return:
    :rtype: dict
    """
    for name, provider in available_providers.items():
        if name != (options['provider'] or name):
            continue

        if provider.accepts(video_path):
            return provider.describe(video_path, options)

    return dict()
