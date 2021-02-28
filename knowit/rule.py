
from .core import Reportable


class Rule(Reportable):
    """Rule abstract class."""

    def __init__(self, name, override=False, **kwargs):
        """Initialize the object."""
        super().__init__(name, **kwargs)
        self.override = override

    def execute(self, props, pv_props, context):
        """How to execute a rule."""
        raise NotImplementedError
