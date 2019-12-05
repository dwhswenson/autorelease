import pytest
from unittest import mock

import os


from autorelease.version import _find_rel_path_for_file

@pytest.mark.parametrize("depth, result", [
    (0, '.'), (1, '..'), (2, '..' + os.sep + '..'),
])
def test_find_rel_path_for_file(depth, result):
    expected = os.path.normpath(result + os.sep + 'setup.cfg')
    assert _find_rel_path_for_file(depth, 'setup.cfg') == expected

@pytest.mark.parametrize("expected", ['./setup.cfg', '../setup.cfg',
                                      '../../setup.cfg'])
def test_find_rel_path_for_file_finds_file(expected):
    with mock.patch('autorelease.version.os.path.isfile',
                    lambda x: x == expected):
        expected = os.path.normpath(expected)  # fix slashes on windows
        assert _find_rel_path_for_file(-1, 'setup.cfg') == expected

def test_find_rel_path_for_file_finds_no_file():
    with mock.patch('autorelease.version.os.path.isfile', lambda x: False):
        assert _find_rel_path_for_file(-1, 'setup.cfg') is None

