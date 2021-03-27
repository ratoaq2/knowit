
from knowit.property import Property


class Quantity(Property):
    """Quantity is a property with unit."""

    def __init__(self, *args: str, unit, data_type=int, **kwargs):
        """Init method."""
        super().__init__(*args, **kwargs)
        self.unit = unit
        self.data_type = data_type

    def handle(self, value, context):
        """Handle value with unit."""
        if not isinstance(value, self.data_type):
            try:
                value = self.data_type(value)
            except ValueError:
                self.report(value, context)
                return

        return value if context.get('no_units') else value * self.unit
