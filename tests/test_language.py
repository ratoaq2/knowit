import typing

import babelfish
import pytest

from knowit.properties import Language

# Issue #219: mediainfo gave a mapping as language, and babelfish called `.split('-')` on it.
MAPPING = {'String': 'en', 'String1': 'English'}


@pytest.mark.parametrize(
    'value',
    [
        MAPPING,
        {'String': 'en', 'String1': 'English', 'String2': 'eng'},
        {},
        ['en', 'fr', 'de'],
        ['en'],
        7,
    ],
    ids=repr,
)
def test_language_handles_non_string_values(context: dict[str, typing.Any], value: typing.Any) -> None:
    # Given
    sut = Language('Language', description='audio language')

    # When
    actual = sut.extract_value({'Language': value}, context)

    # Then
    assert actual == babelfish.Language('und')


def test_language_reports_non_string_values(context: dict[str, typing.Any]) -> None:
    # Given
    sut = Language('Language', description='audio language')
    report: dict[str, typing.Any] = {}
    context['report'] = report
    context['path'] = 'video.mkv'

    # When
    sut.extract_value({'Language': MAPPING}, context)

    # Then: an unhashable value is keyed by its representation instead of by itself
    assert report == {'audio language': {repr(MAPPING): 'video.mkv'}}


@pytest.mark.parametrize(
    'value,expected',
    [
        ('en', babelfish.Language('eng')),
        ('eng', babelfish.Language('eng')),
        ('deu', babelfish.Language('deu')),
        ('pt-BR', babelfish.Language('por', 'BR')),
        ('English', babelfish.Language('eng')),
        ('invalid', babelfish.Language('und')),
    ],
    ids=repr,
)
def test_language_still_handles_string_values(
    context: dict[str, typing.Any], value: str, expected: babelfish.Language
) -> None:
    # Given
    sut = Language('Language', description='audio language')

    # When
    actual = sut.extract_value({'Language': value}, context)

    # Then
    assert actual == expected
