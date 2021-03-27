import typing

from knowit.property import Property

T = typing.TypeVar('T')


class Basic(Property[T]):
    """Basic property to handle int, float and other basic types."""

    def __init__(self, *args: str, data_type: typing.Type, allow_fallback: bool = False, **kwargs):
        """Init method."""
        super().__init__(*args, **kwargs)
        self.data_type = data_type
        self.allow_fallback = allow_fallback

    def handle(self, value, context: typing.MutableMapping):
        """Handle value."""
        if isinstance(value, self.data_type):
            return value

        try:
            return self.data_type(value)
        except ValueError:
            if not self.allow_fallback:
                self.report(value, context)
