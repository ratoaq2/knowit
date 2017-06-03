# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import pytest
import yaml

from knowit.rules import AudioChannelsRule

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
def audiochannels_rule():
    return AudioChannelsRule('audio channels')


@pytest.mark.parametrize('properties,expected', _parameters())
def test_resolution(audiochannels_rule, properties, expected):
    # Given

    # When
    actual = audiochannels_rule.execute(properties, properties)

    # Then
    assert expected == actual
