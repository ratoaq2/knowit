import typing

from knowit.core import Configurable


class AudioCodec(Configurable[str]):
    """Audio codec property."""

    @classmethod
    def _extract_key(cls, value) -> str:
        key = str(value).upper()
        if key.startswith('A_'):
            key = key[2:]

        # only the first part of the word. E.g.: 'AAC LC' => 'AAC'
        return key.split(' ')[0]

    @classmethod
    def _extract_fallback_key(cls, value, key) -> typing.Optional[str]:
        if '/' in key:
            return key.split('/')[0]
        else:
            return None
