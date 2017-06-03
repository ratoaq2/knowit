# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class Rule(object):
    """Rule abstract class."""

    def __init__(self, name, description=None):
        """Constructor."""
        self.name = name
        self._description = description

    @property
    def description(self):
        """Rule description."""
        return self._description or self.name

    def execute(self, props, context):
        """How to execute a rule."""
        raise NotImplementedError
