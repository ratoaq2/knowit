# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

logger = logging.getLogger(__name__)


class Rule(object):
    """Rule abstract class."""

    def execute(self, props):
        """Execute the rule against properties."""
        raise NotImplementedError


class ResolutionRule(Rule):
    """Resolution rule."""

    standard_resolutions = (
        480, 720, 1080, 2160, 4320,
    )
    uncommon_resolutions = (
        240, 288, 360, 576, 960, 1440,
    )
    square = 4. / 3
    wide = 16. / 9

    def execute(self, props):
        """Execute the rule against properties."""
        height = props.get('height')
        width = props.get('width')
        aspect_ratio = props.get('aspect_ratio')
        scan_type = props.get('scan_type')
        if width and height:
            if not scan_type:
                logger.info('Unable to determine resolution: No video scan type')
                return

            ratios = []
            if aspect_ratio:
                ratios.append(aspect_ratio)
                ratios.append(self.wide if aspect_ratio >= self.wide else self.square)
            else:
                ratios.extend([self.wide, self.square])

            for resolutions in (self.standard_resolutions, self.uncommon_resolutions):
                for factor in ratios:
                    actual = int(round(width / factor))
                    for candidate in (actual, height):
                        top = candidate * (1 + 1. / 3)
                        for r in resolutions:
                            if candidate == r:
                                return self._select(candidate, scan_type, props)
                            if candidate <= r <= top:
                                return self._select(r, scan_type, props)

            logger.info('Invalid resolution: %dx%d (%s)', width, height, aspect_ratio)

    @staticmethod
    def _select(resolution, scan_type, props):
        props['resolution'] = '{0}{1}'.format(resolution, scan_type[0].lower())
        return props['resolution']


class AudioChannelsRule(Rule):
    """Audio Channel rule."""

    mapping = {
        1: '1.0',
        2: '2.0',
        6: '5.1',
        # TODO: handle channellayout
        # 7: '6.1',
        8: '7.1',
    }

    def execute(self, props):
        """Execute the rule against properties."""
        count = props.get('channels_count')
        count = max(count) if isinstance(count, list) else count
        if count:
            result = self.mapping.get(count)
            if result:
                props['channels'] = result
            else:
                logger.info('Invalid channels: %d', count)
