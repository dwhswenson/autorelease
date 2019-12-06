import pytest
from autorelease.scripts.bump_dev_version import *

def test_shared_parser():
    parser = shared_parser()
    opts = parser.parse_args([])
    assert opts.index == "https://test.pypi.org/pypi"
    assert opts.conf == "setup.cfg"
    # assert opts.output is None

@pytest.mark.parametrize("v_pypi, v_setup, expected", [
    ("1.0", "1.1", "1.1"),
    ("1.0.dev0", "1.0", "1.0.dev0"),
    ("1.0.rc0", "1.0", "1.0"),
])
def test_select_version(v_pypi, v_setup, expected):
    assert select_version(v_pypi, v_setup) == expected


@pytest.mark.parametrize("version_str, expected", [
    ("1.0", "1.0.dev0"), ("1.0.dev0", "1.0.dev1"),
])
def test_bump_dev_version(version_str, expected):
    assert bump_dev_version(version_str) == expected
