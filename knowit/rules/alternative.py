
from knowit.rule import Rule


class AlternativeRule(Rule):
    """Alternative rule."""

    def __init__(self, name: str, prop_name: str, **kwargs):
        """Initialize an AlternativeRule."""
        super().__init__(name, **kwargs)
        self.prop_name = prop_name

    def execute(self, props, pv_props, context):
        """Execute the rule against properties."""
        if f'_{self.prop_name}' in pv_props and self.prop_name not in props:
            return pv_props.get(f'_{self.prop_name}')
