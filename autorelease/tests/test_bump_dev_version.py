import pytest
from autorelease.scripts.bump_dev_version import *
import autorelease.scripts.bump_dev_version as bump_mod
import autorelease.version as version_mod

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


def test_get_version_info_reuses_loaded_conf(tmp_path, monkeypatch):
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        "[metadata]\n"
        "name = mypkg\n"
        "version = 1.2.3.dev0\n"
    )

    real_get_setup_cfg = bump_mod.get_setup_cfg
    calls = {"count": 0}

    def counted_get_setup_cfg(*args, **kwargs):
        calls["count"] += 1
        return real_get_setup_cfg(*args, **kwargs)

    def unexpected_get_setup_cfg(*args, **kwargs):
        raise AssertionError("setup.cfg was reloaded")

    monkeypatch.setattr(bump_mod, "get_setup_cfg", counted_get_setup_cfg)
    monkeypatch.setattr(version_mod, "get_setup_cfg", unexpected_get_setup_cfg)
    monkeypatch.setattr(bump_mod, "get_latest_pypi", lambda *args: "1.2.2")

    conf, package, v_setup, v_pypi = bump_mod.get_version_info(
        str(setup_cfg), "https://example.invalid/pypi"
    )

    assert calls["count"] == 1
    assert conf.get("metadata", "name") == "mypkg"
    assert package == "mypkg"
    assert v_setup == "1.2.3.dev0"
    assert v_pypi == "1.2.2"


def test_get_version_info_malformed_cfg(tmp_path):
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        "[metadata\n"
        "name = badpkg\n"
        "version = 0.0.0\n"
    )

    with pytest.raises(RuntimeError, match="Unable to parse setup config"):
        bump_mod.get_version_info(
            str(setup_cfg), "https://example.invalid/pypi"
        )
