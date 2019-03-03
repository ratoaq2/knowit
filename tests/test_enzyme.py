# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from knowit import know

from . import (
    assert_expected,
    id_func,
    mediafiles
)


@pytest.mark.parametrize('media', mediafiles.get_json_media('enzyme'), ids=id_func)
def test_enzyme_provider(enzyme, media, options):
    # Given
    enzyme[media.video_path] = media.input_data

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)


@pytest.mark.parametrize('media', mediafiles.get_real_media('enzyme'), ids=id_func)
def test_enzyme_provider_real_media(media, options):
    # Given
    options['provider'] = 'enzyme'
    options['fail_on_error'] = False

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
