# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest

from knowit.rules import ResolutionRule

from . import (
    assert_expected,
    parameters_from_yaml,
)


@pytest.fixture
def resolution_rule():
    return ResolutionRule('resolution')


@pytest.mark.parametrize('expected,input', parameters_from_yaml(__name__))
def test_resolution(resolution_rule, context, expected, input):
    # Given

    # When
    actual = resolution_rule.execute(input, input, context)

    # Then
    assert_expected(expected, actual)
