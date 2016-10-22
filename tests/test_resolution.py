# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import pytest
import yaml

from knowit.properties import ResolutionRule

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _parameters():
    parameters = []
    input_file = os.path.join(__location__, __name__.split('.')[-1] + '.yml')
    with open(input_file, 'r') as stream:
        data = yaml.load(stream)

    for expected, array in data.items():
        for properties in array:
            parameters.append([properties, expected])

    return parameters


@pytest.fixture
def resolution_rule():
    return ResolutionRule()


@pytest.mark.parametrize('properties,expected', _parameters())
def test_resolution(resolution_rule, properties, expected):
    # Given
    context = dict()

    # When
    actual = resolution_rule.handle(properties, context)

    # Then
    assert expected == actual
