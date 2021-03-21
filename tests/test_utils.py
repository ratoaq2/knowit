from unittest.mock import patch

import pytest

from knowit.utils import detect_os


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
def test_detect_os_is_windows(os_name, sys_platform, expected):
    with patch('knowit.utils.os') as mock_os:
        mock_os.name = os_name
        with patch('knowit.utils.sys') as mock_sys:
            mock_sys.platform = sys_platform
            assert detect_os() == expected
