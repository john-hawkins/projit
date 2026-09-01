import json
import os

import pandas as pd
import pytest

from projit import ascii_plot as ascii_plot_module
from projit import latex_table
from projit import template
from projit import utils
from projit.config import config_file
from projit.config import config_folder
from projit.config import execution_file
from projit.config import lock_file
from projit.config import tag_file
from projit.projit import init
from projit.projit import load


@pytest.fixture
def project(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    return init("default", "demo", "demo project")


def test_write_and_open_config_round_trip(tmp_path):
    config_path = tmp_path / "config.yaml"
    payload = {"project_name": "demo", "description": "round trip"}

    utils.write_config(payload, str(config_path))

    assert utils.open_config(str(config_path)) == payload


def test_add_experiment_overwrite_cleans_results(project):
    project.add_experiment("baseline", "old.py")
    project.add_dataset("validation", "val.csv")
    project.add_result("baseline", "rmse", 0.5)
    project.add_result("baseline", "rmse", 0.4, dataset="validation")

    project.add_experiment("baseline", "new.py")

    assert project.experiments == [("baseline", "new.py")]
    assert "baseline" not in project.results
    assert project.dataresults["validation"] == {}


def test_accessors_and_path_helpers_cover_edge_cases(project):
    project.add_dataset("relative", "data/train.csv")
    project.add_dataset("absolute", "/tmp/train.csv")
    project.add_dataset("remote", "http://example.com/train.csv")
    project.add_dataset("bucket", "s3://bucket/train.csv")
    project.add_experiment("baseline", "train.py")

    assert project.dataset_exists("relative") is True
    assert project.experiment_exists("baseline") is True
    assert project.validate_asset("dataset", "relative") is True
    assert project.validate_asset("experiment", "baseline") is True
    assert project.validate_asset("unknown", "baseline") is False
    assert project.get_path_to_dataset("relative") == "data/train.csv"
    assert project.get_path_to_dataset("absolute") == "/tmp/train.csv"
    assert project.get_path_to_dataset("remote") == "http://example.com/train.csv"
    assert project.get_path_to_dataset("bucket") == "s3://bucket/train.csv"


def test_missing_accessors_raise_exceptions(project):
    with pytest.raises(Exception, match="Named dataset 'missing'"):
        project.get_dataset("missing")

    with pytest.raises(Exception, match="Named parameter 'missing'"):
        project.get_param("missing")

    with pytest.raises(Exception, match="Hyper parameters for experiment 'missing'"):
        project.get_hyperparam("missing")

    with pytest.raises(Exception, match="No results for dataset: missing"):
        project.get_results("missing")

    with pytest.raises(Exception, match="Cannot end experiment: 'missing'"):
        project.end_experiment("missing", "exec-id")


def test_start_experiment_persists_execution_and_tags(project):
    project.add_experiment("train-model", "train.py")

    execution_id = project.start_experiment(
        "train-model",
        "train.py",
        params={"lr": 0.1},
        tags={"stage": "baseline"},
    )
    project.end_experiment("train-model", execution_id, hyperparams={"depth": 3})

    reloaded = load(config_folder)

    assert execution_id in reloaded.executions["train-model"]
    assert reloaded.executions["train-model"][execution_id]["params"] == {"lr": 0.1}
    assert reloaded.executions["train-model"][execution_id]["hyperparams"] == {"depth": 3}
    assert reloaded.get_tags("experiment", "train-model", ["stage", "owner"]) == ["baseline", ""]


def test_reload_restores_saved_project_state(project):
    project.add_param("target", "label")
    project.name = "mutated"
    project.params = {}

    project.reload()

    assert project.name == "demo"
    assert project.get_param("target") == "label"


def test_lock_file_lifecycle(project):
    lock_path = os.path.join(project.path, lock_file)

    project.initiate_lock()
    assert os.path.isfile(lock_path)

    project.release_lock()
    assert not os.path.exists(lock_path)


def test_template_profiles_and_padding(capsys):
    template.profiles = {}

    template.start_profile("fit")
    template.end_profile("fit")
    template.print_profiles()

    captured = capsys.readouterr()
    assert "Computation Time Profile" in captured.err
    assert "fit" in captured.err
    assert template.padded("fit", 6) == "fit   "


def test_ascii_plot_and_arange_cover_logscale_branch():
    plot = ascii_plot_module.ascii_plot(
        [1, 10, 100],
        xdata=[1, 2, 3],
        logscale=True,
        pch="*",
        xlabel="Epoch",
        ylabel="Loss",
        width=20,
        height=10,
    )

    assert "Loss" in plot
    assert "Epoch" in plot
    assert "1/inf" in plot
    assert "*" in plot
    assert ascii_plot_module.arange(1, 5, 1) == [1, 2, 3, 4]


def test_latex_output_escapes_special_characters(capsys):
    df = pd.DataFrame([{"experiment": "model_1", "rmse%": 0.25}])

    latex_table.print_latex(df, "Score & Summary")

    captured = capsys.readouterr()
    assert "\\caption{Score & Summary}" in captured.out
    assert "model\\_1" in captured.out
    assert "rmse\\%" in captured.out


def test_save_writes_core_execution_and_tag_files(project):
    project.add_experiment("baseline", "train.py")
    project.add_tags("experiment", "baseline", {"stage": "prod"})
    execution_id = project.start_experiment("baseline", "train.py", params={"seed": 7})
    project.end_experiment("baseline", execution_id, hyperparams={"depth": 2})

    config_path = os.path.join(project.path, config_file)
    executions_path = os.path.join(project.path, execution_file)
    tags_path = os.path.join(project.path, tag_file)

    with open(config_path) as fh:
        config_payload = json.load(fh)
    with open(executions_path) as fh:
        executions_payload = json.load(fh)
    with open(tags_path) as fh:
        tags_payload = json.load(fh)

    assert config_payload["name"] == "demo"
    assert "executions" not in config_payload
    assert execution_id in executions_payload["baseline"]
    assert tags_payload["experiment"]["baseline"]["stage"] == "prod"
