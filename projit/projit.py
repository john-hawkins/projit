import json
import re
import os

from .config import config_file
from .config import config_folder
from .template import load_template
from .utils import locate_projit_config

##########################################################################################

class Projit:
    """
    Projit Class.
    This is a data structure to contain the core elements of a data science 
    project. It will permit loose coupling between processes and experiments
    but provide a simple overarching structure for communication and 
    documentation.
    """

    def __init__(self, path, name, desc="", experiments=[], datasets={}):
        """
        Initialise a projit project class.

        :param path: The path to the project file.
        :type path: string, required

        :param name: The project name
        :type name: string, required

        :param desc: The project description
        :type desc: string, optional

        :param experiments: The array of experiments
        :type experiments: Array, optional

        :param datasets: The dictionary of datasets 'name':'path'
        :type datasets: Dictionary, optional

        :return: None 
        :rtype: None 
        """
        self.path = path
        self.name = name
        self.desc = desc
        self.experiments = experiments
        self.datasets = datasets

    def add_experiment(self, name, path):
        """
        Add information of a new experiment to the project. 
        """
        self.experiments.append( (name, path) )

    def add_dataset(self, name, path):
        """
        Add a named dataset to the project.
        """
        self.datasets[name] = path

    def get_dataset(self, name):
        if name in self.datasets:
            return self.datasets[name]
        else:
            raise Exception("ERROR: Named dataset '%s' not available:"%name)

    def save(self):
        """
        Save your projit project. 
        """
        path_to_json = self.path + "/" + config_file
        with open(path_to_json, 'w') as outfile:
            json.dump(self.__dict__, outfile)

##########################################################################################
def load(config_path):
    """
    This function allows you to instantiate a Projit project from an existing config_path
    The config path must contain the required config file that contains the required fields.

    Note: This function will always overwrite the path variable in the object so the instance
    is aware of where it is relative to the config directory.

    :param config_path: The path to the projit configuration
    :type config_path: string, required

    :return: Projit Object
    :rtype: Projit
    """
    path_to_json = config_path + "/" + config_file
    with open(path_to_json) as f:
        _dict = json.load(f)
    _object = Projit(**_dict)
    _object.path = config_path
    return _object

##########################################################################################
def projit_load():
    return load( locate_projit_config() )

##########################################################################################
def init(template, name, desc=""):
    """
    Initialise a new projit project.
    Create the config directory and write the project config there.

    :param name: The name of the project
    :type name: string, required

    :param desc: The project description
    :type desc: string, required

    :return: Projit Object
    :rtype: Projit
    """
    os.mkdir(config_folder)
    project = Projit(config_folder, name, desc)
    project.save()
    temp = load_template(template)
    for d in temp['dirs']:
        if not os.path.isdir(d):
            os.mkdir(d) 
    return project

##########################################################################################

