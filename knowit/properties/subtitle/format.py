
from ...property import Configurable


class SubtitleFormat(Configurable):
    """Subtitle Format property."""

    @classmethod
    def _extract_key(cls, value):
        key = str(value).upper()
        if key.startswith('S_'):
            key = key[2:]

        return key.split('/')[-1]
