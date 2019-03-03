# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from tests import mediafiles
from knowit import know

from . import assert_expected, id_func


@pytest.mark.parametrize('media', mediafiles.get_xml_media('mediainfo'), ids=id_func)
def test_mediainfo_provider(mediainfo, media, options):
    # Given
    mediainfo[media.video_path] = media.input_data

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)


@pytest.mark.parametrize('media', mediafiles.get_real_media('mediainfo'), ids=id_func)
def test_mediainfo_provider_real_media(media, options):
    # Given
    options['provider'] = 'mediainfo'

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)


@pytest.mark.parametrize('media', mediafiles.get_real_media('mediainfo'), ids=id_func)
def test_mediainfo_provider_real_media_cli(mediainfo_cli, media, options):
    # Given
    options['provider'] = 'mediainfo'

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
