import re
import typing
from datetime import timedelta

from knowit.property import Property


class Duration(Property[timedelta]):
    """Duration property."""

    duration_re = re.compile(r'(?P<hours>\d{1,2}):'
                             r'(?P<minutes>\d{1,2}):'
                             r'(?P<seconds>\d{1,2})(?:\.'
                             r'(?P<millis>\d{3})'
                             r'(?P<micro>\d{3})?\d*)?')

    def __init__(self, name: str, resolution: float = 1, *args, **kwargs):
        """Initialize a Duration."""
        super().__init__(name, *args, **kwargs)
        self.resolution = resolution

    def handle(self, value, context: typing.MutableMapping):
        """Return duration as timedelta."""
        if isinstance(value, timedelta):
            return value
        elif isinstance(value, int):
            return timedelta(microseconds=value * self.resolution)
        try:
            return timedelta(microseconds=int(float(value) * self.resolution))
        except ValueError:
            pass

        try:
            h, m, s, ms, mc = self.duration_re.match(value).groups('0')
            return timedelta(hours=int(h), minutes=int(m), seconds=int(s), milliseconds=int(ms), microseconds=int(mc))
        except ValueError:
            pass

        self.report(value, context)
