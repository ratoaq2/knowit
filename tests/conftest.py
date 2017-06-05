# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import pytest
from six import text_type

from knowit.config import Config


@pytest.fixture
def context():
    return {
        'profile': 'default',
    }


@pytest.fixture
def video_path(tmpdir):
    return text_type(tmpdir.ensure('video.mkv'))


@pytest.fixture
def config():
    return Config.build()
