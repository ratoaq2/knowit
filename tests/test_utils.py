from unittest.mock import patch

import pytest
import os

from knowit.utils import detect_os, build_path_candidates


@pytest.mark.parametrize(
    'os_name, sys_platform, expected', [
        ('nt', None, 'windows'),
        ('dos', None, 'windows'),
        ('os2', None, 'windows'),
        ('ce', None, 'windows'),
        (None, 'darwin', 'macos'),
        (None, None, 'unix'),
    ]
)
def test_detect_os(os_name, sys_platform, expected):
    with patch('knowit.utils.os') as mock_os:
        mock_os.name = os_name
        with patch('knowit.utils.sys') as mock_sys:
            mock_sys.platform = sys_platform
            assert detect_os() == expected


@pytest.mark.parametrize(
    'os_family, path, names, expected', [
        (
            'windows',
            r'C:\Application;C:\Program Files\Application',
            ('some.dll', 'some.exe', 'another.exe'),
            [
                r'C:\Application\some.dll',
                r'C:\Application\some.exe',
                r'C:\Application\another.exe',
                r'C:\Program Files\Application\some.dll',
                r'C:\Program Files\Application\some.exe',
                r'C:\Program Files\Application\another.exe',
            ],
        ),
        (
                'macos',
                '/usr/sbin:/usr/bin:/sbin:/bin',
                ('some.dll', 'binary', 'another_binary'),
                [
                    'some.dll',
                    'binary',
                    'another_binary',
                ],
        ),
        (
                'linux',
                '/usr/sbin:/usr/bin:/sbin:/bin',
                ('some.dll', 'binary', 'another_binary'),
                [
                    'some.dll',
                    'binary',
                    'another_binary',
                ],
        ),
    ],
)
def test_build_path_candidates_for_specified_os(names, os_family, path, expected):
    with patch('knowit.utils.os') as mock_os:
        mock_os.environ = {'PATH': path}
        mock_os.path = os.path  # don't mock os.path functions
        candidates = build_path_candidates(names, os_family)
        assert list(candidates) == expected
