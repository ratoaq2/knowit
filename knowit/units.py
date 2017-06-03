# -*- coding: utf-8 -*-

from pint import UnitRegistry
from six import text_type


def _build_unit_registry():
    ureg = UnitRegistry()
    ureg.define('FPS = 1 * hertz')

    return ureg


def format_quantity(quantity):
    """Human friendly format."""
    unit = quantity.units
    if unit != 'bit':
        if unit == 'hertz':
            return _format_quantity(quantity.magnitude, unit='Hz', precision=1)

        root_unit = quantity.to_root_units().units
        if root_unit == 'bit':
            return _format_quantity(quantity.magnitude)
        if root_unit == 'bit / second':
            return _format_quantity(quantity.magnitude, unit='bps', precision=1)

    return text_type(quantity)


def _format_quantity(num, unit='B', binary=False, precision=2):
    fmt_pattern = '{value:3.%sf} {prefix}{affix}{unit}' % precision
    factor = 1024. if binary else 1000.
    binary_affix = 'i' if binary else ''
    for prefix in ('', 'K', 'M', 'G', 'T', 'P', 'E', 'Z'):
        if abs(num) < factor:
            return fmt_pattern.format(value=num, prefix=prefix, affix=binary_affix, unit=unit)
        num /= factor

    return fmt_pattern.format(value=num, prefix='Y', affix=binary_affix, unit=unit)


units = _build_unit_registry()
