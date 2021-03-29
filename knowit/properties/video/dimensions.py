
import re
import typing

from knowit.core import Property


class VideoDimensions(Property[int]):
    """Dimensions property."""

    def __init__(self, *args: str, dimension='width' or 'height', **kwargs):
        """Initialize the object."""
        super().__init__(*args, **kwargs)
        self.dimension = dimension

    dimensions_re = re.compile(r'(?P<width>\d+)x(?P<height>\d+)')

    def handle(self, value, context) -> typing.Optional[int]:
        """Handle ratio."""
        match = self.dimensions_re.match(value)
        if match:
            return int(match.groupdict().get(self.dimension))

        self.report(value, context)
        return None
