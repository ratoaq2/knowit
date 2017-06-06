# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .core import Reportable


class Rule(Reportable):
    """Rule abstract class."""

    def execute(self, props, pv_props, context):
        """How to execute a rule."""
        raise NotImplementedError
