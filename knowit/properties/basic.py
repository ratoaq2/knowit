# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from logging import NullHandler, getLogger

from six import text_type

from .property import Property

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Basic(Property):
    """Basic property to handle int, float and other basic types."""

    def __init__(self, name, data_type, **kwargs):
        """Init method."""
        super(Basic, self).__init__(name, **kwargs)
        self.data_type = data_type

    def handle(self, value):
        """Handle value."""
        if isinstance(value, self.data_type):
            return value

        try:
            return self.data_type(text_type(value))
        except ValueError:
            logger.info('Invalid %s: %r', self.description, value)
