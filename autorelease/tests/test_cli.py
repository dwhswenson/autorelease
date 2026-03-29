from click.testing import CliRunner

import autorelease.scripts.cli as cli_mod


def test_metadata_version(monkeypatch):
    monkeypatch.setattr(
        cli_mod, "get_setup_version",
        lambda _conf, default_version=None: "1.2.3"
    )
    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["metadata", "version"])
    assert result.exit_code == 0
    assert result.output.strip() == "1.2.3"


def test_metadata_name(monkeypatch):
    monkeypatch.setattr(
        cli_mod, "get_setup_name",
        lambda _conf, default_name=None: "mypackage"
    )
    runner = CliRunner()
    result = runner.invoke(cli_mod.cli, ["metadata", "name"])
    assert result.exit_code == 0
    assert result.output.strip() == "mypackage"


def test_metadata_cli_name_and_version(tmp_path):
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        "[metadata]\n"
        "name = mypkg\n"
        "version = 1.2.3.dev0\n"
    )

    runner = CliRunner()
    name_result = runner.invoke(
        cli_mod.cli, ["metadata", "name", "--conf", str(setup_cfg)]
    )
    version_result = runner.invoke(
        cli_mod.cli, ["metadata", "version", "--conf", str(setup_cfg)]
    )

    assert name_result.exit_code == 0
    assert name_result.output == "mypkg\n"
    assert version_result.exit_code == 0
    assert version_result.output == "1.2.3.dev0\n"


def test_metadata_cli_missing_file(tmp_path):
    missing_cfg = tmp_path / "missing.cfg"
    runner = CliRunner()

    name_result = runner.invoke(
        cli_mod.cli, ["metadata", "name", "--conf", str(missing_cfg)]
    )
    version_result = runner.invoke(
        cli_mod.cli, ["metadata", "version", "--conf", str(missing_cfg)]
    )

    assert name_result.exit_code != 0
    assert f"Unable to find setup config: {missing_cfg}" in name_result.output
    assert version_result.exit_code != 0
    assert f"Unable to find setup config: {missing_cfg}" in version_result.output


def test_metadata_cli_missing_fields(tmp_path):
    no_name_cfg = tmp_path / "setup_no_name.cfg"
    no_name_cfg.write_text(
        "[metadata]\n"
        "version = 2.0.0\n"
    )
    no_version_cfg = tmp_path / "setup_no_version.cfg"
    no_version_cfg.write_text(
        "[metadata]\n"
        "name = pkg-without-version\n"
    )

    runner = CliRunner()
    missing_name_result = runner.invoke(
        cli_mod.cli, ["metadata", "name", "--conf", str(no_name_cfg)]
    )
    missing_version_result = runner.invoke(
        cli_mod.cli, ["metadata", "version", "--conf", str(no_version_cfg)]
    )

    assert missing_name_result.exit_code != 0
    assert f"Missing [metadata] name in {no_name_cfg}" in missing_name_result.output
    assert missing_version_result.exit_code != 0
    assert (
        f"Missing [metadata] version in {no_version_cfg}"
        in missing_version_result.output
    )


def test_metadata_cli_malformed_cfg(tmp_path):
    setup_cfg = tmp_path / "setup.cfg"
    setup_cfg.write_text(
        "[metadata\n"
        "name = badpkg\n"
        "version = 0.0.0\n"
    )

    runner = CliRunner()
    name_result = runner.invoke(
        cli_mod.cli, ["metadata", "name", "--conf", str(setup_cfg)]
    )
    version_result = runner.invoke(
        cli_mod.cli, ["metadata", "version", "--conf", str(setup_cfg)]
    )

    assert name_result.exit_code != 0
    assert f"Unable to parse setup config: {setup_cfg}" in name_result.output
    assert version_result.exit_code != 0
    assert (
        f"Unable to parse setup config: {setup_cfg}"
        in version_result.output
    )
