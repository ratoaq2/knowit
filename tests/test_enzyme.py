# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import glob
import os

import pytest
import yaml

import knowit

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def _parameters():
    parameters = []
    input_dir = os.path.join(__location__, 'enzyme')
    yml_files = [f for f in glob.glob(os.path.join(input_dir, '*.yml'))]

    for input_file in yml_files:
        with open(input_file, 'r') as stream:
            data = yaml.load(stream)

        raw = data['input']
        expected = data['expected']
        parameters.append([raw, expected])

    return parameters


@pytest.mark.parametrize('raw,expected', _parameters())
def test_enzyme_provider(raw, expected):
    # Given
    options = dict(provider='enzyme', raw=False)

    # When
    actual = knowit.knowit(raw, options)

    # Then
    assert expected == actual
