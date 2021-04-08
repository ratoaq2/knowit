import pytest

from knowit.provider import Provider
from knowit.units import units


@pytest.mark.parametrize(
    'frame_rate', [
        pytest.param(3.4 * units.fps, id='Frame rate with magnitude'),
        pytest.param(1, id='Frame rate without magnitude'),
    ],
)
def test_provider_validate_track_frame_rate(frame_rate):
    track = {'frame_rate': 0}
    Provider._validate_track('video', track)
