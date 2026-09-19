import pickle
import typing

import pytest

from knowit import KnowitException, know

from . import JsonMedia, Media, assert_expected, id_func, mediafiles


@pytest.mark.parametrize('media', mediafiles.get_json_media('enzyme'), ids=id_func)
def test_enzyme_provider(enzyme: dict[str, typing.Any], media: JsonMedia, options: dict[str, typing.Any]) -> None:
    # Given
    enzyme[media.video_path] = media.input_data

    # When
    actual = know(media.video_path, options)

    # Then
    assert_expected(media.expected_data, actual, options)
    assert pickle.loads(pickle.dumps(actual)) == actual


@pytest.mark.parametrize('media', mediafiles.get_real_media('enzyme'), ids=id_func)
def test_enzyme_provider_real_media(media: Media, options: dict[str, typing.Any]) -> None:
    # Given
    options['provider'] = 'enzyme'
    options['fail_on_error'] = False

    # When
    if not media.expected_data:
        with pytest.raises(KnowitException):
            know(media.video_path, options)
    else:
        actual = know(media.video_path, options)

        # Then
        assert_expected(media.expected_data, actual, options)
        assert pickle.loads(pickle.dumps(actual)) == actual
