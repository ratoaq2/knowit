# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

import enzyme
import pytest
import knowit

from . import (
    Mock,
    assert_expected,
    parameters_from_yaml,
)


@pytest.mark.parametrize('expected,input', parameters_from_yaml(__name__, expected_key='expected', input_key='input'))
def test_enzyme_provider(monkeypatch, video_path, expected, input):
    # Given
    options = dict(provider='enzyme')
    expected['path'] = video_path
    expected['size'] = os.path.getsize(video_path)
    expected['provider'] = 'Enzyme {0}'.format(enzyme.__version__)
    monkeypatch.setattr('enzyme.MKV', Mock())
    monkeypatch.setattr('knowit.utils.todict', lambda mkv: input)
    container = os.path.splitext(video_path)[1][1:]

    # When
    actual = knowit.know(video_path, options)

    # Then
    assert container == actual.pop('container', None)
    assert_expected(expected, actual)
