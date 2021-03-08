# -*- coding: utf-8 -*-
import os
import yaml
from os import path

from .config import config_folder
from .config import properties_file
from .config import data_file
from .config import experiments_file

"""
    projit.utils: Core utility functions of the projit package.
"""

########################################################################################
def locate_projit_config():
    """
        Find a path to a projit project config, or return empty string.
    """
    projit_folder = ""
    current_dir = os.getcwd()
    generator = walk_up(current_dir)
    for pa, dirs, files in generator:
        if config_folder in dirs:
            projit_folder = pa + "/" + config_folder 
            break
    return projit_folder


########################################################################################
def walk_up(bottom):
    """ 
    mimic os.walk, but walk 'up'
    instead of down the directory tree
    """
    bottom = path.realpath(bottom)
    try:
        names = os.listdir(bottom)
    except Exception as e:
        print(e)
        return
    dirs, nondirs = [], []
    for name in names:
        if path.isdir(path.join(bottom, name)):
            dirs.append(name)
        else:
            nondirs.append(name)
    yield bottom, dirs, nondirs
    new_path = path.realpath(path.join(bottom, '..'))
    if new_path == bottom:
        return
    for x in walk_up(new_path):
        yield x

########################################################################################
def create_properties(project_name, descrip):
    config = {}
    config['project_name'] = project_name
    config['description'] = descrip
    return config

########################################################################################
def initialise_project(name,descrip):
    os.mkdir(config_folder)
    props = create_properties(name, descrip)
    write_properties(config_folder, props)

########################################################################################
def get_properties(pathway):
    return open_config(pathway + "/" + properties_file)

########################################################################################
def write_properties(pathway, props):
    filename = (pathway + "/" + properties_file)
    write_config(props, filename)

########################################################################################
def get_data_config(pathway):
    return open_config(pathway + "/" + data_file)

########################################################################################
def get_experiments(pathway):
    return open_config(pathway + "/" + experiments_file)

########################################################################################
def open_config(filename):
    with open(filename) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config


########################################################################################
def write_config(config, filename):
    with open(filename, 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False, allow_unicode=True)


########################################################################################
