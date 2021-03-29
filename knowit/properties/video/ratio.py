
import re
import typing
from decimal import Decimal

from knowit.core import Property
from knowit.utils import round_decimal


class Ratio(Property[Decimal]):
    """Ratio property."""

    def __init__(self, *args: str, unit=None, **kwargs):
        """Initialize the object."""
        super().__init__(*args, **kwargs)
        self.unit = unit

    ratio_re = re.compile(r'(?P<width>\d+)[:/](?P<height>\d+)')

    def handle(self, value, context) -> typing.Optional[Decimal]:
        """Handle ratio."""
        match = self.ratio_re.match(value)
        if match:
            width, height = match.groups()
            if (width, height) == ('0', '1'):  # identity
                return Decimal('1.0')

            result = round_decimal(Decimal(width) / Decimal(height), min_digits=1, max_digits=3)
            if self.unit:
                result *= self.unit

            return result

        self.report(value, context)
        return None
