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
    gena = walk_up("./tests")
    path, dirs, files = gena.__next__()
    assert len(dirs) == 1 # pytest will create a __pycache__ folder
    path, dirs, files = gena.__next__()
    # Back in the project root. dirs should contain ['projit','tests']
    assert 'projit' in dirs
    assert 'tests' in dirs

#################################################################
def test_locate_projit_config():
    assert locate_projit_config() == ""

#################################################################
def test_projit_init():
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
#def test_experiment_executions():
#    testdir = "temp_test_dir_xyz"
#    os.mkdir(testdir)
#    os.chdir(testdir)
#    project = proj.init("default", "test execution", "execution test")
#    exec_id = project.start_experiment("Initial Exp", "experiments/exp_one.py", params={})
#    time.sleep(2)
#    project.end_experiment("Initial Exp", exec_id, hyperparams={})
#    exec_id = project.start_experiment("Initial Exp", "experiments/exp_one.py", params={})
#    time.sleep(6)
#    project.end_experiment("Initial Exp", exec_id, hyperparams={})
#    #Start an additioning hanging execution - ensure it is excluded from stats
#    exec_id = project.start_experiment("Initial Exp", "experiments/exp_one.py", params={})
#    execs, mean_time = project.get_experiment_execution_stats("Initial Exp")
#    assert execs == 2
#    assert mean_time == pytest.approx(4, 1.0)
#    os.chdir("../") 
#    shutil.rmtree(testdir)



#################################################################
def test_project_params():
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
