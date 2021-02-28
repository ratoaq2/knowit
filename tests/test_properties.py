# -*- coding: utf-8 -*-

import pytest

from knowit import properties

from . import parameters_from_yaml


@pytest.mark.parametrize('name,expected,input', parameters_from_yaml(__name__))
def test_resolution(config, context, name, expected, input):
    # Given
    prop_class = getattr(properties, name)
    sut = prop_class(config, name)
    track = {name: input}

    # When
    actual = sut.extract_value(track, context)

    # Then
    assert expected == actual
