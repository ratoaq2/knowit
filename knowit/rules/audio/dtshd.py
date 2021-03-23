
from knowit.rule import Rule


class DtsHdRule(Rule):
    """DTS-HD rule."""

    @classmethod
    def _redefine(cls, props, name, index):
        actual = props.get(name)
        if isinstance(actual, list):
            value = actual[index]
            if value is None:
                del props[name]
            else:
                props[name] = value

    def execute(self, props, pv_props, context):
        """Execute the rule against properties."""
        if props.get('codec') == 'DTS' and props.get('profile') in ('Master Audio', 'High Resolution Audio'):
            props['codec'] = 'DTS-HD'
