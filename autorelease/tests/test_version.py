import pytest
from unittest import mock

import os


from autorelease.version import (
    ConfigParserError, _find_rel_path_for_file, get_setup_cfg,
    get_setup_name, get_setup_version
)

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


def test_get_setup_name_and_version(tmp_path):
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        "[metadata]\n"
        "name = mypkg\n"
        "version = 1.2.3.dev0\n"
    )
    conf = get_setup_cfg(str(tmp_path), "setup.cfg")
    assert get_setup_name(conf, default_name=None) == "mypkg"
    assert get_setup_version(conf, default_version=None) == "1.2.3.dev0"


def test_get_setup_name_and_version_missing_file(tmp_path):
    default_name = "default-name"
    default_version = "0.0.0"
    conf = get_setup_cfg(str(tmp_path), "setup.cfg")
    assert get_setup_name(conf, default_name=default_name) == default_name
    assert get_setup_version(
        conf, default_version=default_version
    ) == default_version


def test_get_setup_name_and_version_missing_fields(tmp_path):
    setup_cfg_no_name = tmp_path / "setup_no_name.cfg"
    setup_cfg_no_name.write_text(
        "[metadata]\n"
        "version = 2.0.0\n"
    )
    conf_no_name = get_setup_cfg(str(tmp_path), "setup_no_name.cfg")
    assert get_setup_name(
        conf_no_name, default_name="default-name"
    ) == "default-name"
    assert get_setup_version(
        conf_no_name, default_version=None
    ) == "2.0.0"

    setup_cfg_no_version = tmp_path / "setup_no_version.cfg"
    setup_cfg_no_version.write_text(
        "[metadata]\n"
        "name = pkg-without-version\n"
    )
    conf_no_version = get_setup_cfg(str(tmp_path), "setup_no_version.cfg")
    assert get_setup_version(
        conf_no_version, default_version="0.0.0"
    ) == "0.0.0"
    assert get_setup_name(
        conf_no_version, default_name=None
    ) == "pkg-without-version"


def test_get_setup_name_and_version_malformed_cfg(tmp_path):
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        "[metadata\n"
        "name = badpkg\n"
        "version = 0.0.0\n"
    )

    with pytest.raises(ConfigParserError):
        get_setup_cfg(str(tmp_path), "setup.cfg")
