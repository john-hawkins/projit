"""
New tests written as part of the PLAN.md implementation.
Covers T-01 through T-49 from the plan.
"""
import io
import os
import sys
import time
import json

import pandas as pd
import pytest

from projit import ascii_plot as ascii_plot_module
from projit import latex_table
from projit import template
from projit import utils
from projit.ascii_plot import arange, ascii_plot
from projit.config import config_folder, lock_file
from projit.latex_table import clean_data_for_latex, print_latex
from projit.projit import Projit, init, load
from projit.utils import locate_projit_config, walk_up


# ---------------------------------------------------------------------------
# Shared fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return init("default", "demo", "demo project")


# ===========================================================================
# T-01 / T-02  get_execution_times — datetime parsing resilience  (BUG-1)
# ===========================================================================

def test_execution_times_no_microseconds(project):
    """T-01: Timestamps without microseconds must not crash get_execution_times."""
    project.add_experiment("exp", "run.py")
    exec_id = project.start_experiment("exp", "run.py")

    # Manually overwrite the stored timestamps to drop the microsecond component
    execs = project.executions["exp"][exec_id]
    execs["start"] = "2024-01-01 10:00:00"
    execs["end"] = "2024-01-01 10:00:05"
    project.executions["exp"][exec_id] = execs
    project.save()

    times = project.get_execution_times("exp")
    assert times == [5]


def test_execution_times_malformed_timestamp_skipped(project):
    """T-02: Malformed timestamp records are skipped; valid records remain."""
    project.add_experiment("exp", "run.py")
    exec_id = project.start_experiment("exp", "run.py")

    # Inject a bad record alongside a valid one
    project.executions["exp"]["bad-id"] = {
        "start": "NOT_A_DATE",
        "end": "ALSO_NOT_A_DATE",
        "githash": "",
        "params": {},
    }
    # Complete the real execution (valid timestamps)
    project.end_experiment("exp", exec_id)

    times = project.get_execution_times("exp")
    assert len(times) == 1   # Only the valid record should be counted
    assert times[0] >= 0


# ===========================================================================
# T-03  get_results — correctness with many experiments
# ===========================================================================

def test_get_results_many_experiments(project):
    """T-03: get_results with 50+ experiments returns correct DataFrame."""
    for i in range(55):
        name = f"exp_{i}"
        project.add_experiment(name, "run.py")
        project.add_result(name, "rmse", float(i) * 0.01)

    df = project.get_results()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 55
    assert "experiment" in df.columns
    assert list(df.columns)[0] == "experiment"


# ===========================================================================
# T-04  get_results — experiment with no results
# ===========================================================================

def test_get_results_experiment_with_no_results(project):
    """T-04: An experiment with no results appears as a row without crashing."""
    project.add_experiment("no_results_exp", "run.py")
    df = project.get_results()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 1
    assert df.loc[0, "experiment"] == "no_results_exp"


# ===========================================================================
# T-05  add_result for unregistered experiment — raises (fixed, see issue 13)
# ===========================================================================

def test_add_result_for_unregistered_experiment(project):
    """T-05: add_result for an unregistered experiment raises an exception."""
    with pytest.raises(Exception):
        project.add_result("ghost_exp", "rmse", 0.9)


def test_add_result_for_unregistered_dataset(project):
    """T-05b: add_result with a valid experiment but unregistered dataset raises."""
    project.add_experiment("exp1", "run.py")
    with pytest.raises(Exception):
        project.add_result("exp1", "rmse", 0.9, dataset="ghost_dataset")


# ===========================================================================
# T-06  add_tags — merges with existing tags (BUG-5 verification)
# ===========================================================================

def test_add_tags_merges_with_existing(project):
    """T-06: Adding tags twice preserves previously set tags."""
    project.add_experiment("exp", "run.py")
    project.add_tags("experiment", "exp", {"stage": "baseline"})
    project.add_tags("experiment", "exp", {"team": "ml"})

    tags = project.get_tags("experiment", "exp", ["stage", "team"])
    assert tags == ["baseline", "ml"]


# ===========================================================================
# T-07  get_tags — order matches request, not storage
# ===========================================================================

def test_get_tags_returns_in_requested_order(project):
    """T-07: Tags are returned in the order the caller requests."""
    project.add_dataset("ds", "data.csv")
    project.add_tags("dataset", "ds", {"a": "alpha", "b": "beta", "c": "gamma"})

    result = project.get_tags("dataset", "ds", ["c", "a", "b"])
    assert result == ["gamma", "alpha", "beta"]


# ===========================================================================
# T-08  get_tags — missing key returns empty string
# ===========================================================================

def test_get_tags_missing_key_returns_empty_string(project):
    """T-08: Requesting a tag key that was never set returns empty string."""
    project.add_experiment("exp", "run.py")
    project.add_tags("experiment", "exp", {"stage": "dev"})

    result = project.get_tags("experiment", "exp", ["stage", "nonexistent"])
    assert result == ["dev", ""]


# ===========================================================================
# T-09 / T-10 / T-11  is_complete_path  (BUG-6)
# ===========================================================================

def test_is_complete_path_https(project):
    """T-09: https:// URL is recognised as a complete path."""
    assert project.is_complete_path("https://example.com/data.csv") is True


def test_is_complete_path_http_relative_not_complete(project):
    """T-10: A relative path that starts with 'http' is NOT a complete path."""
    assert project.is_complete_path("http_local/data.csv") is False


def test_is_complete_path_gs_bucket(project):
    """T-11: gs:// URL is recognised as a complete path."""
    assert project.is_complete_path("gs://bucket/data.csv") is True


def test_is_complete_path_s3(project):
    assert project.is_complete_path("s3://bucket/data.csv") is True


def test_is_complete_path_absolute(project):
    assert project.is_complete_path("/absolute/local/path.csv") is True


def test_is_complete_path_relative(project):
    assert project.is_complete_path("relative/path.csv") is False


# ===========================================================================
# T-12  add_hyperparam — experiment not found raises exception
# ===========================================================================

def test_add_hyperparam_missing_experiment_raises(project):
    """T-12: add_hyperparam for a non-existent experiment must raise."""
    with pytest.raises(Exception, match="No experiment called"):
        project.add_hyperparam("ghost", {"lr": 0.01})


# ===========================================================================
# T-13  get_hyperparam — registered experiment, no hyperparams stored
# ===========================================================================

def test_get_hyperparam_registered_experiment_no_params(project):
    """T-13: get_hyperparam raises when no hyperparams have been stored."""
    project.add_experiment("exp", "run.py")
    with pytest.raises(Exception, match="Hyper parameters for experiment 'exp'"):
        project.get_hyperparam("exp")


# ===========================================================================
# T-14  clean_experimental_results — clears both results and dataresults
# ===========================================================================

def test_clean_experimental_results_clears_all_locations(project):
    """T-14: clean_experimental_results removes from results and dataresults."""
    project.add_experiment("exp", "run.py")
    project.add_dataset("val", "val.csv")
    project.add_result("exp", "rmse", 0.5)
    project.add_result("exp", "rmse", 0.4, dataset="val")

    project.clean_experimental_results("exp")

    assert "exp" not in project.results
    assert "exp" not in project.dataresults.get("val", {})


# ===========================================================================
# T-15  end_experiment — wrong execution ID raises exception
# ===========================================================================

def test_end_experiment_wrong_id_raises(project):
    """T-15: end_experiment with a non-existent ID raises an exception."""
    project.add_experiment("exp", "run.py")
    project.start_experiment("exp", "run.py")

    with pytest.raises(Exception, match="Cannot end experiment"):
        project.end_experiment("exp", "totally-wrong-id")


# ===========================================================================
# T-16  get_mean_execution_time — zero completed executions returns 0
# ===========================================================================

def test_get_mean_execution_time_zero_completed(project):
    """T-16: Mean execution time is 0 when there are no completed executions."""
    project.add_experiment("exp", "run.py")
    assert project.get_mean_execution_time("exp") == 0


def test_get_mean_execution_time_incomplete_only(project):
    """T-16b: Only started (not ended) executions → still returns 0."""
    project.add_experiment("exp", "run.py")
    project.start_experiment("exp", "run.py")  # never ended
    assert project.get_mean_execution_time("exp") == 0


# ===========================================================================
# T-17  validate_asset — unknown asset type returns False
# ===========================================================================

def test_validate_asset_unknown_type(project):
    """T-17: validate_asset returns False for unrecognised asset types."""
    project.add_experiment("exp", "run.py")
    assert project.validate_asset("pipeline", "exp") is False
    assert project.validate_asset("", "exp") is False


# ===========================================================================
# T-18  Lock file lifecycle — create and release
# ===========================================================================

def test_lock_lifecycle(project):
    """T-18: Lock file is created by initiate_lock and deleted by release_lock."""
    lock_path = os.path.join(project.path, lock_file)
    assert not os.path.exists(lock_path)

    project.initiate_lock()
    assert os.path.isfile(lock_path)

    project.release_lock()
    assert not os.path.exists(lock_path)


def test_lock_release_idempotent(project):
    """T-18b: release_lock is safe to call when no lock file exists."""
    project.release_lock()  # no lock — should not raise


# ===========================================================================
# T-19  save + reload round-trip — full fidelity
# ===========================================================================

def test_save_reload_round_trip(project):
    """T-19: Full state is preserved after save and reload."""
    project.add_experiment("exp", "run.py")
    project.add_dataset("train", "data/train.csv")
    project.add_param("target", "label")
    project.add_result("exp", "rmse", 0.33)
    project.add_tags("experiment", "exp", {"stage": "prod"})
    exec_id = project.start_experiment("exp", "run.py", params={"seed": 42})
    project.end_experiment("exp", exec_id, hyperparams={"depth": 5})

    reloaded = load(config_folder)

    assert reloaded.name == "demo"
    # JSON round-trip converts tuples → lists
    assert reloaded.experiments == [["exp", "run.py"]]
    assert reloaded.datasets == {"train": "data/train.csv"}
    assert reloaded.get_param("target") == "label"
    assert exec_id in reloaded.executions["exp"]
    assert reloaded.get_tags("experiment", "exp", ["stage"]) == ["prod"]
    df = reloaded.get_results()
    assert df.loc[0, "rmse"] == 0.33


# ===========================================================================
# T-20 / T-21  rm_dataset / rm_experiment — non-existent names are silent no-ops
# ===========================================================================

def test_rm_dataset_nonexistent_is_no_op(project):
    """T-20: Removing a dataset that doesn't exist should not raise."""
    project.add_dataset("real", "data.csv")
    project.rm_dataset("nonexistent")
    assert "real" in project.datasets


def test_rm_experiment_nonexistent_is_no_op(project):
    """T-21: Removing an experiment that doesn't exist should not raise."""
    project.add_experiment("real", "run.py")
    project.rm_experiment("nonexistent")
    assert project.experiment_exists("real")


# ===========================================================================
# T-22 / T-23 / T-24  get_dataset / get_param / add_param overwrite
# ===========================================================================

def test_get_dataset_not_registered_raises(project):
    """T-22: get_dataset raises for an unregistered dataset name."""
    with pytest.raises(Exception, match="Named dataset 'missing'"):
        project.get_dataset("missing")


def test_get_param_not_registered_raises(project):
    """T-23: get_param raises for an unregistered parameter name."""
    with pytest.raises(Exception, match="Named parameter 'missing'"):
        project.get_param("missing")


def test_add_param_overwrite(project):
    """T-24: add_param overwrites an existing parameter with the new value."""
    project.add_param("lr", 0.1)
    project.add_param("lr", 0.01)
    assert project.get_param("lr") == 0.01


# ===========================================================================
# T-25 / T-26  locate_projit_config — finds config up the tree
# ===========================================================================

def test_locate_config_two_levels_up(tmp_path, monkeypatch):
    """T-25: locate_projit_config finds .projit two levels above cwd."""
    monkeypatch.chdir(tmp_path)
    init("default", "ancestor", "test")

    deep = tmp_path / "sub" / "deeper"
    deep.mkdir(parents=True)
    monkeypatch.chdir(deep)

    found = locate_projit_config()
    assert found != ""
    assert config_folder in found


def test_locate_config_in_current_dir(tmp_path, monkeypatch):
    """T-26: locate_projit_config finds .projit in the current directory."""
    monkeypatch.chdir(tmp_path)
    init("default", "here", "test")

    found = locate_projit_config()
    assert found != ""
    assert found.endswith(config_folder)


# ===========================================================================
# T-27  walk_up — terminates cleanly at filesystem root
# ===========================================================================

def test_walk_up_terminates_at_root():
    """T-27: walk_up starting at filesystem root terminates without recursion error."""
    results = list(walk_up("/"))
    assert len(results) >= 1


# ===========================================================================
# T-28  write_properties + get_properties — round-trip with non-ASCII chars
# ===========================================================================

def test_properties_round_trip_non_ascii(tmp_path, monkeypatch):
    """T-28: Properties file handles non-ASCII characters correctly."""
    monkeypatch.chdir(tmp_path)
    from projit.utils import initialise_project, get_properties, write_properties
    initialise_project("Ünïcödé Näme", "Déscription with ñ")
    cfg = get_properties(config_folder)
    assert cfg["project_name"] == "Ünïcödé Näme"
    assert cfg["description"] == "Déscription with ñ"


# ===========================================================================
# T-29 / T-30 / T-31 / T-32 / T-33  ascii_plot edge cases  (BUG-2)
# ===========================================================================

def test_ascii_plot_uniform_y_no_div_zero():
    """T-29: ascii_plot with all identical y-values does not raise ZeroDivisionError."""
    result = ascii_plot([5, 5, 5, 5], width=20, height=5)
    assert isinstance(result, str)


def test_ascii_plot_uniform_x_no_div_zero():
    """T-30: ascii_plot with all identical x-values does not raise ZeroDivisionError."""
    result = ascii_plot([1, 2, 3], xdata=[1, 1, 1], width=20, height=5)
    assert isinstance(result, str)


def test_ascii_plot_single_data_point():
    """T-31: ascii_plot with a single data point produces output without crashing."""
    result = ascii_plot([42], width=20, height=5)
    assert isinstance(result, str)
    assert len(result) > 0


def test_ascii_plot_negative_values():
    """T-32: ascii_plot with negative y-values renders without error."""
    result = ascii_plot([-10, -5, 0, 5, 10], width=20, height=5)
    assert isinstance(result, str)


def test_ascii_plot_logscale_non_positive():
    """T-33: ascii_plot in log scale with non-positive values does not crash."""
    result = ascii_plot([0, 1, 10, 100], logscale=True, width=20, height=5)
    assert isinstance(result, str)


# ===========================================================================
# T-34 / T-35  arange edge cases
# ===========================================================================

def test_arange_step_larger_than_range():
    """T-34: arange returns empty or single element when step > range."""
    result = arange(1, 2, 10)
    assert result == []


def test_arange_fractional_step():
    """T-35: arange with fractional step matches expected values."""
    result = arange(0, 1, 0.25)
    assert len(result) == 4
    for expected, actual in zip([0.0, 0.25, 0.5, 0.75], result):
        assert abs(actual - expected) < 1e-9


# ===========================================================================
# T-36 / T-37 / T-38  LaTeX escaping  (BUG-11)
# ===========================================================================

def test_clean_data_for_latex_backslash():
    """T-36: Backslash is converted to \\textbackslash{}."""
    result = clean_data_for_latex("path\\to\\file")
    assert "\\textbackslash{}" in result
    assert result == "path\\textbackslash{}to\\textbackslash{}file"


def test_clean_data_for_latex_tilde():
    """T-37: Tilde is converted to \\textasciitilde{}."""
    result = clean_data_for_latex("a~b")
    assert result == "a\\textasciitilde{}b"


def test_clean_data_for_latex_backslash_then_brace():
    """T-36b: \\{ in input → \\textbackslash{}\\{ (brace is also escaped)."""
    result = clean_data_for_latex("\\{")
    assert result == "\\textbackslash{}\\{"


def test_clean_data_for_latex_all_specials():
    """T-38: All currently handled special characters are correctly escaped."""
    input_str = "100% $5 #1 ^2 a&b c_d {x} y"
    result = clean_data_for_latex(input_str)
    assert "\\%" in result
    assert "\\$" in result
    assert "\\#" in result
    assert "\\^" in result
    assert "\\&" in result
    assert "\\_" in result
    assert "\\{" in result
    assert "\\}" in result


# ===========================================================================
# T-39 / T-40  print_latex
# ===========================================================================

def test_print_latex_empty_dataframe(capsys):
    """T-39: print_latex with an empty DataFrame produces a valid LaTeX table."""
    df = pd.DataFrame(columns=["experiment"])
    print_latex(df, "Empty Table")
    captured = capsys.readouterr()
    assert "\\begin{table}" in captured.out
    assert "\\end{table}" in captured.out
    assert "Empty Table" in captured.out


def test_print_latex_numeric_floats(capsys):
    """T-40: print_latex renders numeric float values correctly."""
    df = pd.DataFrame([{"experiment": "run1", "rmse": 0.123456}])
    print_latex(df, "Scores")
    captured = capsys.readouterr()
    assert "run1" in captured.out
    assert "0.123456" in captured.out


# ===========================================================================
# T-41 / T-42 / T-43  template.py profiling
# ===========================================================================

def test_profiles_independent_names():
    """T-41: Profiles for different names track independently."""
    template.reset_profiles()
    template.start_profile("step_a")
    time.sleep(0.01)
    template.end_profile("step_a")
    template.start_profile("step_b")
    time.sleep(0.02)
    template.end_profile("step_b")

    assert "step_a" in template.profiles
    assert "step_b" in template.profiles
    # step_b should take longer than step_a
    assert template.profiles["step_b"]["total"] > template.profiles["step_a"]["total"]
    template.reset_profiles()


def test_print_profiles_no_profiles(capsys):
    """T-42: print_profiles with no recorded profiles does not raise."""
    template.reset_profiles()
    template.print_profiles()  # should not raise
    captured = capsys.readouterr()
    assert "Computation Time Profile" in captured.err
    template.reset_profiles()


def test_padded_string_longer_than_width():
    """T-43: padded() with a string longer than padto does not crash."""
    result = template.padded("this_is_a_very_long_key", padto=5)
    # Returns the string with negative padding (spaces subtracted), result starts with original
    assert result.startswith("this_is_a_very_long_key")


# ===========================================================================
# T-44 / T-45  CLI task_tag — malformed input  (BUG-8)
# ===========================================================================

def test_task_tag_no_equals_sign_exits_with_error(project):
    """T-44: task_tag with a token missing '=' prints error and exits 1."""
    from projit.cli import task_tag
    with pytest.raises(SystemExit) as exc_info:
        task_tag(project, "experiment", "exp", "noequals")
    assert exc_info.value.code == 1


def test_task_tag_empty_key_exits_with_error(project):
    """T-45: task_tag with an empty key ('=value') prints error and exits 1."""
    from projit.cli import task_tag
    project.add_experiment("exp", "run.py")
    with pytest.raises(SystemExit) as exc_info:
        task_tag(project, "experiment", "exp", "=value")
    assert exc_info.value.code == 1


def test_task_tag_value_with_equals_is_accepted(project):
    """T-45b: task_tag splits only on the first '=', so values may contain '='."""
    from projit.cli import task_tag
    project.add_experiment("exp", "run.py")
    task_tag(project, "experiment", "exp", "url=http://x.com?a=1")
    tags = project.get_tags("experiment", "exp", ["url"])
    assert tags == ["http://x.com?a=1"]


# ===========================================================================
# T-46 / T-47 / T-48  CLI formatting helpers
# ===========================================================================

def test_print_results_markdown_long_experiment_names(capsys):
    """T-46: Markdown table adapts column width to long experiment names."""
    from projit.cli import print_results_markdown
    long_name = "a" * 50
    df = pd.DataFrame([{"experiment": long_name, "rmse": 0.5}])
    print_results_markdown("Results", df)
    captured = capsys.readouterr()
    assert long_name in captured.out


def test_print_results_markdown_empty_dataframe(capsys):
    """T-47: print_results_markdown with empty DataFrame prints header without crash."""
    from projit.cli import print_results_markdown
    df = pd.DataFrame(columns=["experiment"])
    print_results_markdown("Empty Results", df)
    captured = capsys.readouterr()
    assert "Empty Results" in captured.out


def test_filler_zero_length():
    """T-48: filler() with zero difference returns empty string."""
    from projit.cli import filler
    assert filler(5, 5) == ""
    assert filler(0, 0) == ""


# ===========================================================================
# T-49  CLI exit code for successful init  (BUG-3)
# ===========================================================================

def test_cli_init_exits_zero(tmp_path, monkeypatch):
    """T-49: A successful 'projit init' command exits with code 0 (not 1)."""
    from projit.cli import cli_main
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["projit", "init", "MyProject"])
    with pytest.raises(SystemExit) as exc_info:
        cli_main()
    assert exc_info.value.code == 0, (
        f"Expected exit code 0, got {exc_info.value.code} — BUG-3 may not be fixed"
    )
