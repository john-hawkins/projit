import pandas as pd
import json
import re
import os

from .config import config_file
from .config import config_folder
from .template import load_template
from .utils import locate_projit_config
from .pdf import PDF

##########################################################################################

class Projit:
    """
    Projit Class.
    This is a data structure to contain the core elements of a data science 
    project. It will permit loose coupling between processes and experiments
    but provide a simple overarching structure for communication and 
    documentation.
    """

    def __init__(self, path, name, desc="", experiments=[], datasets={}, results={}, params={}):
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

        :param results: The dictionary of datasets 'experiment':{'metric':'value'}
        :type results: Dictionary of Dictionary, optional

        :param params: A dictionary of additional parameters share across experiments. 
                       For example: target variable name, identifier column.
        :type params: Dictionary, optional

        :return: None 
        :rtype: None 
        """
        self.path = path
        self.name = name
        self.desc = desc
        self.experiments = experiments
        self.datasets = datasets
        self.results = results
        self.params = params


    def get_root_path(self):
        """
        Get the path to where the project folder is located
        """
        return self.path[0:len(self.path) - len(config_folder)]


    def add_experiment(self, name, path):
        """
        Add information of a new experiment to the project. 
        Then save the project configuration.
        This function will overwrite an experiment of the same name
        and delete any previous results.

        :param name: The experiment name
        :type name: string, required

        :param path: The path to the experiment.
        :type path: string, required
        """
        for elem in self.experiments: 
            if elem[0] == name:
                self.experiments.remove(elem)
                self.results[name] = {}
        self.experiments.append( (name, path) )
        self.save()


    def add_dataset(self, name, path):
        """
        Add a named dataset to the project.

        :param name: The dataset name
        :type name: string, required

        :param path: The path to the data set (either local path, URL or S3 Bucket)
        :type path: string, required
        """
        self.datasets[name] = path
        self.save()

    def add_param(self, name, value):
        """
        Add a parameter to the project.

        :param name: The parameter name
        :type name: string, required

        :param value: The value taken by that parameter
        :type value: Any
        """
        self.params[name] = value 
        self.save()


    def add_result(self, experiment, metric, value):
        """
        Add results from an experiment to the project.

        :param name: The experiment name
        :type name: string, required

        :param metric: The name of the metric we are adding.
        :type path: string, required

        :param value: The value of the metric to add.
        :type value: float, required
        """
        if experiment in self.results:
            rez = self.results[experiment]
        else:
            rez = {}
        rez[metric] = value
        self.results[experiment] = rez
        self.save()

    def get_results(self):
        df = pd.DataFrame()
        for exp in self.experiments:
            key = exp[0]
            if key in self.results:
                rez = self.results[key]
            else:
                rez = {}
            rez['experiment'] = key
            df = df.append(rez, ignore_index=True)
        return df 

    def get_dataset(self, name):
        if name in self.datasets:
            return self.datasets[name]
        else:
            raise Exception("ERROR: Named dataset '%s' not available:" % name)

    def get_param(self, name):
        if name in self.params:
            return self.params[name]
        else:
            raise Exception("ERROR: Named parameter '%s' is not available:" % name)

    def get_path_to_dataset(self, name):
        ds = self.get_dataset(name)
        if self.is_complete_path(ds):
            return ds
        else:
            return self.create_local_path(ds)

    def is_complete_path(self, path):
        if path[0:1] == "/":
            return True
        if path[0:3] == "s3:":
            return True
        if path[0:4] == "http":
            return True
        return False

    def create_local_path(self, ds):
        return self.get_root_path() + ds

    def save(self):
        """
        Save your projit project. 
        """
        path_to_json = self.path + "/" + config_file
        with open(path_to_json, 'w') as outfile:
            json.dump(self.__dict__, outfile, indent=0)

    def render(self, path):
        results = self.get_results()
        pdf = PDF()
        pdf.setup()
        pdf.add_title(self.name)
        pdf.add_description(self.desc)
        pdf.output(path, 'F')


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
    init_template(template)
    return project

##########################################################################################

def init_template(template):
    if template != "":
        temp = load_template(template)
        for d in temp['dirs']:
            if not os.path.isdir(d):
                os.mkdir(d)


