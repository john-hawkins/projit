import shutil
from projit.utils import walk_up
from projit.utils import locate_projit_config
from projit.projit import initialise_project 
from projit.config import config_folder

def test_walk():
    gena = walk_up("./tests")
    path, dirs, files = gena.__next__()
    assert len(dirs) == 1 # pytest will create a __pycache__ folder
    path, dirs, files = gena.__next__()
    # Back in the project root. dirs should contain ['projit','tests']
    assert 'projit' in dirs
    assert 'tests' in dirs

def test_locate_projit_config():
    assert locate_projit_config() == ""

def test_projit_init():
    initialise_project(["", "", "TEST"])
    assert locate_projit_config() != ""
    shutil.rmtree(config_folder)


