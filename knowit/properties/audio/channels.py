import typing

from knowit.property import Property


class AudioChannels(Property[int]):
    """Audio Channels property."""

    ignored = {
        'object based',  # Dolby Atmos
    }

    def handle(self, value, context) -> typing.Optional[int]:
        """Handle audio channels."""
        if isinstance(value, int):
            return value

        if value.lower() not in self.ignored:
            try:
                return int(value)
            except ValueError:
                self.report(value, context)
        return None
