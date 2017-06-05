# -*- coding: utf-8 -*-

from pint import UnitRegistry


def _build_unit_registry():
    ureg = UnitRegistry()
    ureg.define('FPS = 1 * hertz')

    return ureg


units = _build_unit_registry()
