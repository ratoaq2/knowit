
from knowit.property import Configurable


class VideoCodec(Configurable):
    """Video Codec handler."""

    @classmethod
    def _extract_key(cls, value) -> str:
        key = value.upper().split('/')[-1]
        if key.startswith('V_'):
            key = key[2:]

        return key.split(' ')[-1]
