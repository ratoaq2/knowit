import typing

from knowit.property import Configurable


class VideoProfile(Configurable[str]):
    """Video Profile property."""

    @classmethod
    def _extract_key(cls, value) -> str:
        return value.upper().split('@')[0]


class VideoProfileLevel(Configurable[str]):
    """Video Profile Level property."""

    @classmethod
    def _extract_key(cls, value) -> typing.Union[str, bool]:
        values = str(value).upper().split('@')
        if len(values) > 1:
            value = values[1]
            return value

        # There's no level, so don't warn or report it
        return False


class VideoProfileTier(Configurable[str]):
    """Video Profile Tier property."""

    @classmethod
    def _extract_key(cls, value) -> typing.Union[str, bool]:
        values = str(value).upper().split('@')
        if len(values) > 2:
            return values[2]

        # There's no tier, so don't warn or report it
        return False
