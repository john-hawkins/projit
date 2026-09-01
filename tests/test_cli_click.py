"""
Tests for the click-based CLI (Issue #14).

All tests use click.testing.CliRunner so they run in-process without spawning
subprocesses.  Tests are grouped as:

  - Help text / argument validation (no project needed)
  - Integration (project lifecycle via isolated filesystem)
  - Global option propagation (-m, -l, -p)
"""

import os

import pytest
from click.testing import CliRunner

from projit.cli import cli  # will fail until click migration is implemented


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _init_project(runner, name="TestProject"):
    """Initialise a project inside the runner's current isolated directory."""
    result = runner.invoke(cli, ["init", name])
    assert result.exit_code == 0, f"init failed: {result.output}"
    return result


# ===========================================================================
# Top-level help
# ===========================================================================

def test_top_level_help_lists_all_subcommands():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    for cmd in ["init", "update", "add", "tag", "list", "rm", "compare", "plot", "render", "status"]:
        assert cmd in result.output, f"'{cmd}' missing from top-level --help"


def test_no_args_shows_help():
    runner = CliRunner()
    result = runner.invoke(cli, [])
    assert result.exit_code == 0
    assert "Usage" in result.output or "Commands" in result.output


def test_version_flag():
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    from projit import __version__
    assert __version__ in result.output


def test_dash_h_is_synonymous_with_help():
    """projit -h and projit --help must produce the same output."""
    runner = CliRunner()
    r1 = runner.invoke(cli, ["--help"])
    r2 = runner.invoke(cli, ["-h"])
    assert r1.exit_code == 0
    assert r2.exit_code == 0
    assert r1.output == r2.output


# ===========================================================================
# init --help
# ===========================================================================

def test_init_help_describes_name_and_template():
    runner = CliRunner()
    result = runner.invoke(cli, ["init", "--help"])
    assert result.exit_code == 0
    assert "NAME" in result.output or "name" in result.output.lower()
    assert "template" in result.output.lower()


# ===========================================================================
# add --help and validation
# ===========================================================================

def test_add_help_shows_asset_choices():
    runner = CliRunner()
    result = runner.invoke(cli, ["add", "--help"])
    assert result.exit_code == 0
    assert "dataset" in result.output
    assert "experiment" in result.output


def test_add_help_describes_name_and_path():
    runner = CliRunner()
    result = runner.invoke(cli, ["add", "--help"])
    assert result.exit_code == 0
    assert "NAME" in result.output or "name" in result.output.lower()
    assert "PATH" in result.output or "path" in result.output.lower()


def test_add_invalid_asset_shows_error_with_choices():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        result = runner.invoke(cli, ["add", "badtype", "myname", "mypath"])
    assert result.exit_code != 0
    assert "badtype" in result.output or "invalid" in result.output.lower()


# ===========================================================================
# tag --help
# ===========================================================================

def test_tag_help_describes_key_value_format():
    runner = CliRunner()
    result = runner.invoke(cli, ["tag", "--help"])
    assert result.exit_code == 0
    assert "key=value" in result.output or "VALUES" in result.output


def test_tag_help_shows_asset_choices():
    runner = CliRunner()
    result = runner.invoke(cli, ["tag", "--help"])
    assert result.exit_code == 0
    assert "dataset" in result.output
    assert "experiment" in result.output


# ===========================================================================
# list --help and validation
# ===========================================================================

def test_list_help_shows_subcmd_choices():
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--help"])
    assert result.exit_code == 0
    assert "datasets" in result.output
    assert "experiments" in result.output
    assert "results" in result.output


def test_list_help_mentions_tags_option():
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--help"])
    assert result.exit_code == 0
    assert "--tags" in result.output


def test_list_help_mentions_format_options():
    """list --help should note that -m/-l/-p apply."""
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--help"])
    assert result.exit_code == 0
    # Either the global options are shown or the help text references them
    assert any(token in result.output for token in ["-m", "--markdown", "-l", "--latex", "-p", "--precision", "format"])


def test_list_help_describes_dataset_param():
    runner = CliRunner()
    result = runner.invoke(cli, ["list", "--help"])
    assert result.exit_code == 0
    assert "dataset" in result.output.lower()


def test_list_invalid_subcmd_shows_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        result = runner.invoke(cli, ["list", "badsubcmd"])
    assert result.exit_code != 0
    assert "badsubcmd" in result.output or "invalid" in result.output.lower()


# ===========================================================================
# rm --help
# ===========================================================================

def test_rm_help_shows_asset_choices():
    runner = CliRunner()
    result = runner.invoke(cli, ["rm", "--help"])
    assert result.exit_code == 0
    assert "dataset" in result.output
    assert "experiment" in result.output


def test_rm_help_mentions_dot_for_all():
    runner = CliRunner()
    result = runner.invoke(cli, ["rm", "--help"])
    assert result.exit_code == 0
    assert "." in result.output


# ===========================================================================
# compare --help
# ===========================================================================

def test_compare_help_mentions_comma_separated_datasets():
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "--help"])
    assert result.exit_code == 0
    assert "comma" in result.output.lower() or "DATASETS" in result.output


def test_compare_help_describes_metric():
    runner = CliRunner()
    result = runner.invoke(cli, ["compare", "--help"])
    assert result.exit_code == 0
    assert "METRIC" in result.output or "metric" in result.output.lower()


# ===========================================================================
# plot --help
# ===========================================================================

def test_plot_help_shows_property_choices():
    runner = CliRunner()
    result = runner.invoke(cli, ["plot", "--help"])
    assert result.exit_code == 0
    assert "execution" in result.output
    assert "hyperparam" in result.output
    assert "result" in result.output


def test_plot_help_mentions_metric_is_conditional():
    runner = CliRunner()
    result = runner.invoke(cli, ["plot", "--help"])
    assert result.exit_code == 0
    assert "METRIC" in result.output or "metric" in result.output.lower()


# ===========================================================================
# render --help
# ===========================================================================

def test_render_help_describes_output_path():
    runner = CliRunner()
    result = runner.invoke(cli, ["render", "--help"])
    assert result.exit_code == 0
    assert "PATH" in result.output or "path" in result.output.lower()
    assert "pdf" in result.output.lower() or "output" in result.output.lower()


# ===========================================================================
# status + update --help
# ===========================================================================

def test_status_has_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["status", "--help"])
    assert result.exit_code == 0


def test_update_has_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["update", "--help"])
    assert result.exit_code == 0


# ===========================================================================
# Integration: project lifecycle
# ===========================================================================

def test_init_creates_projit_directory():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init", "MyProject"])
        assert result.exit_code == 0
        assert os.path.isdir(".projit")


def test_init_duplicate_shows_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(cli, ["init", "First"])
        result = runner.invoke(cli, ["init", "Second"])
        assert result.exit_code != 0
        assert "already exists" in result.output.lower() or "ERROR" in result.output


def test_init_with_template_argument():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["init", "MyProject", "default"])
        assert result.exit_code == 0
        assert os.path.isdir(".projit")


def test_status_shows_project_name():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner, "StatusProject")
        result = runner.invoke(cli, ["status"])
        assert result.exit_code == 0
        assert "StatusProject" in result.output


def test_status_outside_project_shows_init_hint():
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ["status"])
        assert result.exit_code != 0
        assert "init" in result.output.lower() or "not a projit project" in result.output.lower()


def test_add_dataset_then_list():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "dataset", "train", "data/train.csv"])
        result = runner.invoke(cli, ["list", "datasets"])
        assert result.exit_code == 0
        assert "train" in result.output


def test_add_experiment_then_list():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "experiment", "baseline", "train.py"])
        result = runner.invoke(cli, ["list", "experiments"])
        assert result.exit_code == 0
        assert "baseline" in result.output


def test_list_results_empty_project():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        result = runner.invoke(cli, ["list", "results"])
        assert result.exit_code == 0


def test_rm_dataset_with_confirmation():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "dataset", "train", "data/train.csv"])
        result = runner.invoke(cli, ["rm", "dataset", "train"], input="y\n")
        assert result.exit_code == 0


def test_rm_dataset_cancel():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "dataset", "train", "data/train.csv"])
        result = runner.invoke(cli, ["rm", "dataset", "train"], input="n\n")
        assert result.exit_code == 0
        # dataset should still be listed
        list_result = runner.invoke(cli, ["list", "datasets"])
        assert "train" in list_result.output


def test_tag_experiment():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "experiment", "myexp", "train.py"])
        result = runner.invoke(cli, ["tag", "experiment", "myexp", "stage=prod,env=test"])
        assert result.exit_code == 0


def test_tag_invalid_format_shows_error():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "experiment", "myexp", "train.py"])
        result = runner.invoke(cli, ["tag", "experiment", "myexp", "noequals"])
        assert result.exit_code != 0


# ===========================================================================
# Global option propagation
# ===========================================================================

def test_global_markdown_flag_accepted_by_list():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        result = runner.invoke(cli, ["-m", "list", "results"])
        assert result.exit_code == 0


def test_global_latex_flag_accepted_by_list():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        result = runner.invoke(cli, ["-l", "list", "results"])
        assert result.exit_code == 0


def test_global_precision_flag_accepted_by_list():
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        result = runner.invoke(cli, ["-p", "2", "list", "results"])
        assert result.exit_code == 0


def test_global_markdown_produces_markdown_table():
    """With -m, list results should produce a markdown-formatted table."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "experiment", "exp1", "train.py"])
        # Use projit API directly to add a result since CLI doesn't add results
        from projit.projit import load
        from projit.config import config_folder
        p = load(config_folder)
        p.add_result("exp1", "rmse", 0.5)
        result = runner.invoke(cli, ["-m", "list", "results"])
        assert result.exit_code == 0
        assert "|" in result.output  # markdown table separator


def test_global_precision_affects_output():
    """With -p 1, results are displayed at 1 decimal place."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        _init_project(runner)
        runner.invoke(cli, ["add", "experiment", "exp1", "train.py"])
        from projit.projit import load
        from projit.config import config_folder
        p = load(config_folder)
        p.add_result("exp1", "rmse", 0.12345)
        result_p1 = runner.invoke(cli, ["-p", "1", "list", "results"])
        result_p5 = runner.invoke(cli, ["-p", "5", "list", "results"])
        assert result_p1.exit_code == 0
        assert result_p5.exit_code == 0
        # p=1 truncates more aggressively than p=5
        assert "0.12345" not in result_p1.output
