import typing

from knowit.property import Configurable


class YesNo(Configurable[str]):
    """Yes or No handler."""

    yes_values = ('yes', 'true', '1')

    def __init__(self, *args: str, yes=True, no=False, hide_value=None,
                 config: typing.Optional[typing.Mapping[str, typing.Mapping]] = None,
                 config_key: typing.Optional[str] = None,
                 **kwargs):
        """Init method."""
        super().__init__(config or {}, config_key=config_key, *args, **kwargs)
        self.yes = yes
        self.no = no
        self.hide_value = hide_value

    def handle(self, value, context):
        """Handle boolean values."""
        result = self.yes if str(value).lower() in self.yes_values else self.no
        if result == self.hide_value:
            return None

        return super().handle(result, context) if self.mapping else result
