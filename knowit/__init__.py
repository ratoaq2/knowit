#  coding=utf-8
"""Know your media files better."""

__title__ = 'knowit'
__version__ = '0.0.2'
__short_version__ = '.'.join(__version__.split('.')[:2])
__author__ = 'Rato AQ2'
__license__ = 'MIT'
__copyright__ = 'Copyright 2016, Rato AQ2'

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict
