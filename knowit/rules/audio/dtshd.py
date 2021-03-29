import typing

from knowit.core import Rule


class DtsHdRule(Rule):
    """DTS-HD rule."""

    def __init__(self, config: typing.Mapping[str, typing.Mapping], name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.audio_codecs = getattr(config, 'AudioCodec')
        self.audio_profiles = getattr(config, 'AudioProfile')

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
        profile = context.get('profile') or 'default'

        if props.get('codec') == getattr(self.audio_codecs['DTS'], profile) and props.get('profile') in (
                getattr(self.audio_profiles['MA'], profile), getattr(self.audio_profiles['HRA'], profile)):
            props['codec'] = getattr(self.audio_codecs['DTS-HD'], profile)
