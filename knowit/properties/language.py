# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from logging import NullHandler, getLogger
import babelfish

from .property import Property

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class Language(Property):
    """Language property."""

    def handle(self, value):
        """Handle languages."""
        try:
            if len(value) == 3:
                return babelfish.Language.fromalpha3b(value)

            return babelfish.Language.fromietf(value)
        except (babelfish.Error, ValueError):
            pass

        try:
            return babelfish.Language.fromname(value)
        except babelfish.Error:
            pass

        logger.info('Invalid %s: %r', self.description, value)
        return babelfish.Language('und')
