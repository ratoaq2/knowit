# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import glob
import os

try:
    from mock import Mock
except:
    from unittest.mock import Mock

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
def test_enzyme_provider(monkeypatch, video_path, raw, expected):
    # Given
    options = dict(provider='enzyme')
    monkeypatch.setattr('enzyme.MKV', Mock())
    monkeypatch.setattr('knowit.utils.todict', lambda mkv: raw)

    # When
    actual = knowit.know(video_path, options)

    expected['path'] = video_path
    expected['size'] = os.path.getsize(video_path)

    # Then
    assert expected == actual
