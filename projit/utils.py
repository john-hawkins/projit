# -*- coding: utf-8 -*-
import os
import yaml
from os import path

from .config import config_folder

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

def get_raw_config(filename):
    with open(filename) as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
    return config

########################################################################################
def create_properties(project_name):
    config = {}
    config['project_name'] = project_name
    config['description'] = ""
    return config

########################################################################################
def write_config(config, filename):
    with open(filename, 'w') as outfile:
        yaml.dump(config, outfile, default_flow_style=False, allow_unicode=True)


########################################################################################
