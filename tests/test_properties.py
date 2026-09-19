import typing

import pytest

from knowit import properties
from knowit.config import Config

from . import parameters_from_yaml


@pytest.mark.parametrize('name,expected,input', parameters_from_yaml(__name__))
def test_resolution(
    config: Config, context: dict[str, typing.Any], name: str, expected: typing.Any, input: typing.Any
) -> None:
    # Given
    prop_class = getattr(properties, name)
    sut = prop_class(config, name)
    track = {name: input}

    # When
    actual = sut.extract_value(track, context)

    # Then
    assert expected == actual
