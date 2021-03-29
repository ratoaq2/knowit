import typing

import babelfish

from knowit.core import Property


class Language(Property[babelfish.Language]):
    """Language property."""

    def handle(self, value, context: typing.MutableMapping):
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

        self.report(value, context)
        return babelfish.Language('und')
