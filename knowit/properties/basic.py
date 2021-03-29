import typing

from knowit.core import Property

T = typing.TypeVar('T')


class Basic(Property[T]):
    """Basic property to handle int, Decimal and other basic types."""

    def __init__(self, *args: str, data_type: typing.Type,
                 processor: typing.Optional[typing.Callable[[T], T]] = None,
                 allow_fallback: bool = False, **kwargs):
        """Init method."""
        super().__init__(*args, **kwargs)
        self.data_type = data_type
        self.processor = processor or (lambda x: x)
        self.allow_fallback = allow_fallback

    def handle(self, value, context: typing.MutableMapping):
        """Handle value."""
        if isinstance(value, self.data_type):
            return self.processor(value)

        try:
            return self.processor(self.data_type(value))
        except ValueError:
            if not self.allow_fallback:
                self.report(value, context)
