import pathlib
import typing

import pytest

from knowit.provider import Provider, ProviderError
from knowit.providers.ffmpeg import FFmpegExecutor
from knowit.providers.mkvmerge import MkvMergeExecutor
from knowit.units import units


@pytest.mark.parametrize(
    'frame_rate',
    [
        pytest.param(3.4 * units.fps, id='Frame rate with magnitude'),
        pytest.param(1, id='Frame rate without magnitude'),
    ],
)
def test_provider_validate_track_frame_rate(frame_rate: typing.Any) -> None:
    track = {'frame_rate': 0}
    Provider._validate_track('video', track)


@pytest.mark.parametrize(
    ('executor_cls', 'reason'),
    [
        pytest.param(FFmpegExecutor, 'No such file or directory', id='ffprobe'),
        pytest.param(MkvMergeExecutor, 'could not be opened', id='mkvmerge'),
    ],
)
def test_executor_error_keeps_backend_message(
    executor_cls: type[FFmpegExecutor] | type[MkvMergeExecutor], reason: str, tmp_path: pathlib.Path
) -> None:
    # Given
    executor = executor_cls.get_executor_instance()
    if not executor:
        pytest.skip(f'{executor_cls.__name__} backend is not installed')

    # When
    with pytest.raises(ProviderError) as error:
        executor.extract_info(str(tmp_path / 'missing é.mkv'))

    # Then
    assert reason in str(error.value)
