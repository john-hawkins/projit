import os
import pytest
import shutil
import time
from os import path
import pandas as pd
import datatest as dt
import projit.projit as proj
from projit.utils import walk_up
from projit.config import config_folder
from projit.utils import locate_projit_config
from projit.utils import initialise_project 
from projit.utils import get_properties
from projit.utils import write_properties
from projit.projit import projit_load

#################################################################
def test_walk():
    """
    In this test we ensure that the walk function can traverse a 
     directory structure as expected.
    """
    gena = walk_up("./tests")
    path, dirs, files = gena.__next__()
    assert len(dirs) == 1 # pytest will create a __pycache__ folder
    path, dirs, files = gena.__next__()
    # Back in the project root. dirs should contain ['projit','tests']
    assert 'projit' in dirs
    assert 'tests' in dirs

#################################################################
def test_locate_projit_config():
    """
    In this test we ensure that a config file is not found when 
     one does not exist
    """
    assert locate_projit_config() == ""

#################################################################
def test_projit_init():
    """
    In this test we ensure that we can inialise a project properly
    """
    if path.isdir(config_folder):
        shutil.rmtree(config_folder)
    initialise_project("TEST", "TEST")
    assert locate_projit_config() != ""
    cfg = get_properties(config_folder)
    assert cfg['project_name'] == "TEST"
    assert cfg['description'] == "TEST"
    shutil.rmtree(config_folder)

#################################################################
def test_projit_update():
    """
    In this test we ensure that we can update the project properties
    """
    if path.isdir(config_folder):
        shutil.rmtree(config_folder)
    initialise_project("TEST", "TEST")
    assert locate_projit_config() != ""
    cfg = get_properties(config_folder)
    cfg['project_name'] = "TEST2"
    cfg['description'] = "TEST2"
    write_properties(config_folder, cfg)
    cfg2 = get_properties(config_folder)
    assert cfg2['project_name'] == "TEST2"
    assert cfg2['description'] == "TEST2"
    shutil.rmtree(config_folder)

#################################################################
def test_projit_init_v2():
    """
    Second test on project initialisation
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "TEST", "TEST")
    assert locate_projit_config() != ""
    assert project.name == "TEST"
    assert project.desc == "TEST"
    assert path.isdir("data")
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_projit_json_load():
    """
    In this test we see that we can load a JSON file into a Projit object
    """
    project = proj.load("tests")
    assert project.name == "TEST"
    assert project.desc == "TEST"


#################################################################
def test_projit_load():
    """
    In this test we ensure that we load the project file data
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "myproject", "myproject")
    os.mkdir("someotherdir")
    os.chdir("someotherdir")
    theproject = projit_load()
    print("ORIGINAL:", project.path)
    print("LOADED:", theproject.path)
    assert project.name == theproject.name 
    os.chdir("../")
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_template_results():
    """
    In this test we ensure that the project initialisation process 
     will create the right directory in a default setup.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "subdir", "sub dir test")
    assert project.name == "subdir"
    assert path.isdir("data")
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_project_update():
    """
    In this test we ensure that we can update the project properties
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.update_name_description("Name", "DESC")
    assert len(project.name) == 4
    assert project.name == "Name"
    assert project.desc == "DESC"
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_project_update_lock():
    """
    In this test we ensure that the lock mechanism for upating project
     details works correctly.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    # MODIFY THE PROJECT JSON FILE THEN TEST THAT THE
    # - NEW VALUES ARE LOADED BEFORE THE SAVE
    project.params = {"TEST":"TEST"}
    project.save()
    project.update_name_description("Name", "DESC")
    assert len(project.params) == 1
    assert project.name == "Name"
    assert project.desc == "DESC"
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_dataset_add_remove():
    """
    In this test we ensure that the remove functions work for datasets
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_dataset("test",  "pathtofile")
    assert len(project.datasets) == 1
    project.rm_dataset("test")
    assert len(project.datasets) == 0
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_dataset_add_remove_all():
    """
    In this test we ensure that remove with wildcard will remove
     all datasets 
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_dataset("test1",  "pathtofile")
    project.add_dataset("test2",  "pathtofile")
    project.add_dataset("test3",  "pathtofile")
    assert len(project.datasets) == 3
    project.rm_dataset(".")
    assert len(project.datasets) == 0
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_experiment_results():
    """
    In this test we ensure that retrieving results of experiments
     returns the right data structure.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_experiment("test",  "pathtofiles")
    project.add_result("test",  "rmse", 0.5)
    results = project.get_results()
    assert str(type(results)) == "<class 'pandas.core.frame.DataFrame'>"
    assert "experiment" in results.columns
    assert "rmse" in results.columns
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_experiment_remove():
    """
    In this test we ensure that the remove functions work for experiments
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_experiment("test",  "pathtofile")
    project.add_result("test",  "rmse", 0.5)
    assert len(project.experiments) == 1
    project.rm_experiment("test")
    assert len(project.experiments) == 0
    assert len(project.results) == 0
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_experiment_remove_all():
    """
    In this test we ensure that remove with wildcard will remove
     all experiments and results 
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_experiment("test",  "pathtofile")
    project.add_experiment("test2",  "pathtofile")
    project.add_experiment("test3",  "pathtofile")
    project.add_result("test",  "rmse", 0.5)
    project.add_result("test2",  "rmse", 0.5)
    project.add_result("test3",  "rmse", 0.5)
    assert len(project.experiments) == 3
    assert len(project.results) == 3
    project.rm_experiment(".")
    assert len(project.experiments) == 0
    assert len(project.results) == 0
    os.chdir("../")
    shutil.rmtree(testdir)


#################################################################
def test_experiment_executions_zero():
    """
    In this test we ensure that an experiment without registered executions
     is reported as zero.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_experiment("test",  "pathtofile")
    execs, mean_time = project.get_experiment_execution_stats("test")
    assert execs == 0
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_experiment_executions_one():
    """
    In this test we ensure that a single execution is counted.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_experiment("test",  "pathtofile")
    exec_id = project.start_experiment("test", "pathtofile", params={})
    project.end_experiment("test", exec_id, hyperparams={})
    execs, mean_time = project.get_experiment_execution_stats("test")
    assert execs == 1
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_experiment_executions_two():
    """
    In this test we ensure that multiple executions are counted.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_experiment("test",  "pathtofile")
    exec_id = project.start_experiment("test", "pathtofile", params={})
    project.end_experiment("test", exec_id, hyperparams={})
    exec_id = project.start_experiment("test", "pathtofile", params={})
    project.end_experiment("test", exec_id, hyperparams={})
    execs, mean_time = project.get_experiment_execution_stats("test")
    assert execs == 2
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_experiment_executions_incomplete():
    """
    In this test we ensure that incomplete executions are not included
       in the statistics reported about the experiment.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "exp", "exp test")
    project.add_experiment("test",  "pathtofile")
    exec_id = project.start_experiment("test", "pathtofile", params={})
    project.end_experiment("test", exec_id, hyperparams={})
    exec_id = project.start_experiment("test", "pathtofile", params={})
    project.end_experiment("test", exec_id, hyperparams={})
    exec_id = project.start_experiment("test", "pathtofile", params={})
    execs, mean_time = project.get_experiment_execution_stats("test")
    assert execs == 2
    os.chdir("../")
    shutil.rmtree(testdir)


#################################################################
def test_project_params():
    """
    Test that we can set and retrieve project parameters
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "test params", "param test")
    project.add_param("test",  "myval")
    results = project.get_param("test")
    assert results == "myval"
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################
def test_project_hyperparams():
    """
    Test that we can set and retrieve hyperparameters for experiments
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "test params", "param test")
    with pytest.raises(Exception) as e_info:
        project.add_hyperparam("myexp",  "myval")

    project.add_experiment("myexp", "mypath")
    project.add_hyperparam("myexp",  "myval")
    results = project.get_hyperparam("myexp")
    assert results == "myval"
    os.chdir("../")
    shutil.rmtree(testdir)

#################################################################

def test_project_experiment_results():
    """
    Test that experimental results are retrieved correctly.
    """
    testdir = "temp_test_dir_xyz"
    os.mkdir(testdir)
    os.chdir(testdir)
    project = proj.init("default", "test", "test")
    project.add_experiment("myexp", "mypath")
    project.add_dataset("mydata", "datapath")
    project.add_result("myexp", "RMSE", 0.4, "mydata")
    results = project.get_results("mydata")
    dt.validate(
        results.RMSE,
        float
    )
    assert str(type(results)) == "<class 'pandas.core.frame.DataFrame'>"
    dt.validate(
        results.columns,
        {'RMSE', 'experiment'},
    )
    resultslen = len(results)

    # Add a result to the base structure and ensure it does not interfere
    project.add_result("myexp", "RMSE", 0.3)
    results2 = project.get_results("mydata")
    assert str(type(results2)) == "<class 'pandas.core.frame.DataFrame'>"
    dt.validate(
        results2.columns,
        {'RMSE', 'experiment'},
    )
    assert len(results) == len(results2)

    os.chdir("../")
    shutil.rmtree(testdir)

