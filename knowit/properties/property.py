# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from logging import NullHandler, getLogger
from six import PY3, binary_type, text_type

logger = getLogger(__name__)
logger.addHandler(NullHandler())

_visible_chars_table = dict.fromkeys(range(32))


def _is_unknown(value):
    return isinstance(value, text_type) and (not value or value.lower() == 'unknown')


class Property(object):
    """Property class."""

    def __init__(self, name, default=None, private=False, description=None):
        """Init method."""
        self.name = name
        self.default = default
        self.private = private
        self._description = description

    @property
    def description(self):
        """Property description."""
        return self._description or self.name

    def extract_value(self, track):
        """Extract the property value from a given track."""
        value = track.get(self.name)
        if value is None:
            if self.default is None:
                return

            value = self.default

        if isinstance(value, binary_type):
            value = text_type(value)
        if isinstance(value, text_type):
            value = value.translate(_visible_chars_table).strip()
            if _is_unknown(value):
                return

        result = self.handle(value)
        if result is not None and not _is_unknown(result):
            return result

    def handle(self, value):
        """Return the value without any modification."""
        return value

    def _handle(self, value, key, mapping):
        result = mapping.get(key)
        if result is not None:
            return result

        logger.info('Invalid %s: %r', self.description, value)


class MultiValue(Property):
    """Property with multiple values."""

    def __init__(self, prop=None, delimiter='/', handler=None, name=None, **kwargs):
        """Init method."""
        super(MultiValue, self).__init__(prop.name if prop else name, **kwargs)
        self.prop = prop
        self.delimiter = delimiter
        self.handler = handler

    def handle(self, value):
        """Handle properties with multiple values."""
        values = (self._split(value[0], self.delimiter)
                  if len(value) == 1 else value) if isinstance(value, list) else self._split(value, self.delimiter)
        call = self.handler or self.prop.handle
        if len(values) > 1:
            return [call(item) if not _is_unknown(item) else None for item in values]

        return call(values[0])

    @classmethod
    def _split(cls, value, delimiter='/'):
        if value is None:
            return

        v = text_type(value)
        result = map(text_type.strip, v.split(delimiter))
        return list(result) if PY3 else result
