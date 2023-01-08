from logging import NullHandler, getLogger

import babelfish
from trakit.api import trakit

from knowit.core import Rule

logger = getLogger(__name__)
logger.addHandler(NullHandler())


class GuessTitleRule(Rule):
    """Guess properties from track title."""

    def execute(self, props, pv_props, context):
        """Language detection using name."""
        if 'name' in props:
            guessed = trakit(props['name'])
            if guessed:
                return guessed


class LanguageRule(Rule):
    """Language rules."""

    def execute(self, props, pv_props, context):
        """Language detection using name."""
        if 'guessed' not in pv_props:
            return

        guess = pv_props['guessed']
        if 'language' in guess:
            guessed: babelfish.Language = guess['language']
            if 'language' not in props:
                return guessed

            lang: babelfish.Language = props['language']
            if guessed.alpha3 != lang.alpha3 or str(lang).count('-') >= str(guessed).count('-'):
                logger.debug('Discarding %s: Language %r and guessed %r', self.description, lang, guessed)
                return lang

            return guessed
