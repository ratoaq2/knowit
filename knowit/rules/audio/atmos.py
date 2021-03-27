import typing

from knowit.rule import Rule


class AtmosRule(Rule):
    """Atmos rule."""

    def __init__(self, config: typing.Mapping[str, typing.Mapping], name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.audio_codecs = getattr(config, 'AudioCodec')

    def execute(self, props, pv_props, context):
        """Execute the rule against properties."""
        profile = context.get('profile') or 'default'
        format_commercial = pv_props.get('format_commercial')
        if 'codec' in props and format_commercial and 'atmos' in format_commercial.lower():
            props['codec'] = [props['codec'], getattr(self.audio_codecs['ATMOS'], profile)]
