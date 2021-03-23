
from knowit.rule import Rule


class AudioProfileRule(Rule):
    """Audio Profile rule."""

    def execute(self, props, pv_props, context):
        """Execute the rule against properties."""
        if '_profile' in pv_props and 'profile' not in props:
            return pv_props.get('_profile')
