import pickle

import pytest

from knowit import know

from . import (
    assert_expected,
    id_func,
    mediafiles
)


@pytest.mark.parametrize('media', mediafiles.get_json_media('mkvmerge'), ids=id_func)
def test_mkvmerge_provider(mkvmerge, media, options):
    # Given
    mkvmerge[media.video_path] = media.input_data

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual


@pytest.mark.parametrize('media', mediafiles.get_real_media('mkvmerge'), ids=id_func)
def test_mkvmerge_provider_real_media(media, options):
    # Given
    options['provider'] = 'mkvmerge'

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual
