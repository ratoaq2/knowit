# -*- coding: utf-8 -*-

import pytest
from knowit.rules import AudioChannelsRule

from . import (
    assert_expected,
    parameters_from_yaml,
)


@pytest.fixture
def audiochannels_rule():
    return AudioChannelsRule('audio channels')


@pytest.mark.parametrize('expected,input', parameters_from_yaml(__name__))
def test_resolution(audiochannels_rule, context, expected, input):
    # Given

    # When
    actual = audiochannels_rule.execute(input, input, context)

    # Then
    assert_expected(expected, actual)
