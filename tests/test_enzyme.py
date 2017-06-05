# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os

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
    monkeypatch.setattr('enzyme.MKV', Mock())
    monkeypatch.setattr('knowit.utils.todict', lambda mkv: input)

    # When
    actual = knowit.know(video_path, options)

    expected['path'] = video_path
    expected['size'] = os.path.getsize(video_path)

    # Then
    assert_expected(expected, actual)
