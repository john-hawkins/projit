import shutil
from projit.config import config_folder
from projit.utils import walk_up
from projit.utils import locate_projit_config
from projit.utils import initialise_project 
from projit.utils import get_properties
from projit.utils import write_properties

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
    initialise_project("TEST", "TEST")
    assert locate_projit_config() != ""
    cfg = get_properties(config_folder)
    assert cfg['project_name'] == "TEST"
    assert cfg['description'] == "TEST"
    shutil.rmtree(config_folder)

def test_projit_update():
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
