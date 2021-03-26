import typing

from knowit.core import Reportable


T = typing.TypeVar('T')


class Rule(Reportable[T]):
    """Rule abstract class."""

    def __init__(self, name: str, override=False, **kwargs):
        """Initialize the object."""
        super().__init__(name, **kwargs)
        self.override = override

    def execute(self, props, pv_props, context: typing.Mapping):
        """How to execute a rule."""
        raise NotImplementedError
