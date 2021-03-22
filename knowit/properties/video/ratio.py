
import re
import typing

from knowit.property import Property


class Ratio(Property):
    """Ratio property."""

    def __init__(self, name, unit=None, **kwargs):
        """Initialize the object."""
        super().__init__(name, **kwargs)
        self.unit = unit

    ratio_re = re.compile(r'(?P<width>\d+)[:/](?P<height>\d+)')

    def handle(self, value, context) -> typing.Optional[float]:
        """Handle ratio."""
        match = self.ratio_re.match(value)
        if match:
            width, height = match.groups()
            if (width, height) == ('0', '1'):  # identity
                return 1.

            result = round(float(width) / float(height), 3)
            if self.unit:
                result *= self.unit

            return result

        self.report(value, context)
