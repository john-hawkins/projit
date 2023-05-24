from datetime import datetime
import pandas as pd
import numpy as np
import hashlib
import git
import json
import re
import os

from .config import config_file
from .config import execution_file
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

    def __init__(self, 
                 path, 
                 name, 
                 desc="", 
                 experiments=[], 
                 datasets={},
                 results={}, 
                 params={},
                 hyperparams={},
                 dataresults={},
                 executions={}):
        """
        Initialise a projit project object.
        This class will be used for storing and retrieving all data about the project,
        as well as ensuring that it is written to the projit meta-data files.

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

        :param results: The dictionary of results by experiment.
                        Structure: {'experiment':{'metric':'value'}}
        :type results: Dictionary of Dictionary, optional

        :param params: A dictionary of additional parameters share across experiments. 
                       For example: target variable name, identifier column.
        :type params: Dictionary, optional

        :param hyperparams: A dictionary of hyper parameters for experiments. 
                       Structure: {'experiment':{'param':'value', etc}} 
        :type hyperparams: Dictionary, optional

        :param dataresults: The dictionary of results on specific data sets.
                            These are used when you want your experimental results broken
                            down by the datasets. 
                            Structure: {'dataset':{'experiment':{'metric':'value'}}}
        :type dataresults: Dictionary of Dictionary of Dictionary, optional

        :param executions: The dictionary of experiment executions.
                            This structure is used to store all experimental runs.
                            The ID is a HASH of experiment_name and 
                            Structure: {'experiment_name':{
                                             'ID':{ 
                                                 'start':DATETIME, 
                                                 'end':DATETIME,
                                                 'githash':STRING, 
                                                 'params':DICT,
                                                 'hyperparams':DICT
                                              }
                                           }
                                       }
        :type executions: Dictionary of Dictionary of Dictionary, optional

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
        self.hyperparams = hyperparams
        self.dataresults = dataresults
        self.executions = executions


    def get_root_path(self):
        """
        Get the path to where the project folder is located
        """
        return self.path[0:len(self.path) - len(config_folder)]

    def start_experiment(self, name, path, params={}):
        """
        Start an experiment execution.
        This function will create a new experiment if this is the first execution
        otherwise it will simply add a new execution record.
         It returns an identifer for the execution (needed to end the execution)

        :param name: The experiment name (Unique Identifer)
        :type name: string, required

        :param path: The path to the experiment script being executed
        :type path: string, required

        :param params: Optional dictionary of parameters used in the experiment execution
        :type path: Dictionary, option

        :return: id : The Execution ID
        :rtype: String
        """
        if not self.experiment_exists(name):
            self.add_experiment(name, path)

        startdt = str(datetime.now())
        s = name + startdt
        id = hashlib.sha256(s.encode()).hexdigest()
        try:
            repo = git.Repo(search_parent_directories=True)
            ghash = repo.head.object.hexsha
        except git.exc.InvalidGitRepositoryError:
            ghash = ""
        payload = {'start':startdt, 'end':"", 'githash':ghash, 'params':params}
        exper_execs = {}
        if name in self.executions:
            exper_execs = self.executions[name]

        exper_execs[id] = payload
        self.executions[name] = exper_execs 
        self.save()
        return id

    def end_experiment(self, name, id, hyperparams={}):
        """
        End an experiment execution.
        This function require both the experiment name and the hash ID of the previously started execution

        :param name: The experiment name (Unique Identifer)
        :type name: string, required

        :param id: The execution hash ID returned by the function: start_experiment 
        :type id: string, required

        :param hyperparams: Optional dictionary of hyperparameters used in the experiment execution
        :type path: Dictionary, option

        :return: None
        :rtype: None
        """

        if not self.experiment_exists(name):
            raise Exception(f"Projit Experiment Exception: Cannot end experiment: '{name}' -- Experiment not registered")
            
        if name in self.executions:
            exper_execs = self.executions[name]
        else:
            raise Exception(f"Projit Experiment Exception: Cannot end experiment: '{name}' -- Executions not started")

        if id in exper_execs:
            payload = exper_execs[id]
        else:
            raise Exception(f"Projit Experiment Exception: Cannot end experiment: '{name}' -- Executions not started")

        payload['end'] = str(datetime.now())
        payload['hyperparams'] = hyperparams
        exper_execs[id] = payload
        self.executions[name] = exper_execs
        self.save()


    def get_experiment_execution_stats(self, name):
        """
        Given an experiment name
        Return the execution statistics
        """
        if name in self.executions:
            exec_times = self.get_execution_times(name)
            if len(exec_times) > 0:
                return len(exec_times), np.mean(exec_times)
            else:
                return 0, 0
        else:
            return 0, 0

    def get_mean_execution_time(self, name):
        exec_times = self.get_execution_times(name)
        if len(exec_times) > 0:
            return np.mean(exec_times)
        else:
            return 0

    def get_execution_times(self, name):
        if name in self.executions:
            exec_times = []
            for execid, exec in self.executions[name].items():
                if exec["end"] != "":
                    a = datetime.strptime(exec["start"], '%Y-%m-%d %H:%M:%S.%f')
                    b = datetime.strptime(exec["end"], '%Y-%m-%d %H:%M:%S.%f')
                    diff = (b-a).seconds
                    exec_times.append(diff)
            return exec_times
        else:
            return []

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

        :return: None
        :rtype: None
        """
        for elem in self.experiments: 
            if elem[0] == name:
                self.experiments.remove(elem)
                self.clean_experimental_results(name)
        self.experiments.append( (name, path) )
        self.save()


    def experiment_exists(self, name):
        """
        Check if a given experiment is in the data structure

        :param name: The experiment name
        :type name: string, required

        :return: exists
        :rtype: Boolean
        """
        for elem in self.experiments:
            if elem[0] == name:
                return True
        return False

    def clean_experimental_results(self, name):
        """
        Remove all results for a given experiment

        :param name: The experiment name
        :type name: string, required

        :return: None
        :rtype: None
        """
        if name in self.results:
            del self.results[name]
        for dataset in self.dataresults:
            if name in self.dataresults[dataset]:
                del self.dataresults[dataset][name]

    def add_dataset(self, name, path):
        """
        Add a named dataset to the project.

        :param name: The dataset name
        :type name: string, required

        :param path: The path to the data set (either local path, URL or S3 Bucket)
        :type path: string, required

        :return: None
        :rtype: None
        """
        self.datasets[name] = path
        self.save()

    def rm_dataset(self, name):
        """
        Remove a named dataset to the project.

        :param name: The dataset name (or '.' for all datasets)
        :type path: string, required

        :return: None
        :rtype: None
        """
        if name in self.datasets:
            del self.datasets[name] 
            self.save()
        elif name==".":
            del self.datasets
            self.datasets = {}
            self.save()

    def rm_experiment(self, name):
        """
        Remove a named experiment from the project.

        :param name: The experiment name (or '.' for all experiments)
        :type path: string, required

        :return: None
        :rtype: None
        """
        if name==".":
            for elem in self.experiments:
                self.clean_experimental_results(elem[0])
            self.experiments = []
            self.save()
        else:
            for elem in self.experiments:
                if elem[0] == name:
                    self.experiments.remove(elem)
                    self.clean_experimental_results(name)
            self.save()


    def add_param(self, name, value):
        """
        Add a parameter to the project.

        :param name: The parameter name
        :type name: string, required

        :param value: The value taken by that parameter
        :type value: Any

        :return: None
        :rtype: None
        """
        self.params[name] = value 
        self.save()

    def add_hyperparam(self, name, value):
        """
        Add a set of hyper parameters to the project.

        :param name: The experiment name
        :type name: string, required

        :param value: The Dictionary of hyperparameters
        :type value: Dictionary

        :return: None
        :rtype: None
        """
        if self.experiment_exists(name):
            self.hyperparams[name] = value
            self.save()
        else:
            raise Exception("Projit Experiment Exception: No experiment called: '%s' -- Register your experiment first." % name)

    def add_result(self, experiment, metric, value, dataset=None):
        """
        Add results from an experiment to the project.

        They can be overall project results, or associated with a specific dataset

        :param name: The experiment name
        :type name: string, required

        :param metric: The name of the metric we are adding.
        :type metric: string, required

        :param value: The value of the metric to add.
        :type value: float, required

        :param dataset: The dataset against which the results are generated
        :type dataset: string, optional 

        :return: None
        :rtype: None
        """

        if dataset==None:
            if experiment in self.results:
                rez = self.results[experiment]
            else:
                rez = {}
            rez[metric] = value
            self.results[experiment] = rez
        else: 
            if dataset in self.dataresults:
                rez = self.dataresults[dataset]
            else:
                rez = {}
            if experiment in rez:
                rez2 = rez[experiment]
            else:
                rez2 = {}
            rez2[metric] = value
            rez[experiment] = rez2
            self.dataresults[dataset] = rez
        self.save()

    def get_results(self, dataset=None):
        """
        Retrieve the experimental results as a DataFrame.

        They can be overall project results, or associated with a specific dataset

        :param dataset: The dataset against which the results are generated
        :type dataset: string, optional

        :return: DataFrame of results
        :rtype: pandas.DataFrame
        """

        df = pd.DataFrame()
        if dataset==None:
            myresults = self.results
        else:
            if dataset in self.dataresults:
                myresults = self.dataresults[dataset]
            else:
                raise Exception("Projit Dataset Exception: No results for dataset: %s " % dataset)
        for exp in self.experiments:
            key = exp[0]
            if key in myresults:
                rez = myresults[key]
            else:
                rez = {}
            rez['experiment'] = key
            df = pd.concat([df, pd.DataFrame(rez, index=[0])], ignore_index=True)
        # Ensure that the first column in the results is "experiments"
        cols = ["experiment"]
        rest = df.columns.to_list()
        rest.remove('experiment')
        cols.extend(rest)
        return df.loc[:,cols]

    def get_dataset(self, name):
        """
        Retrieve the dataset by name.

        :param name: The dataset to retrieve
        :type name: string, required

        :return: Path to dataset
        :rtype: String
        """
        if name in self.datasets:
            return self.datasets[name]
        else:
            raise Exception("Projit Dataset Exception: Named dataset '%s' not available. Register your dataset" % name)

    def get_param(self, name):
        if name in self.params:
            return self.params[name]
        else:
            raise Exception("Projit Parameter Exception: Named parameter '%s' is not available:" % name)

    def get_hyperparam(self, name):
        if name in self.hyperparams:
            return self.hyperparams[name]
        else:
            raise Exception("Projit Parameter Exception: Hyper parameters for experiemnt '%s' are not available:" % name)

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
        Save your projit project into config files within the projit config dir
        """
        core_props = self.__dict__.copy()
        del core_props['executions']
        path_to_json = self.path + "/" + config_file
        with open(path_to_json, 'w') as outfile:
            json.dump(core_props, outfile, indent=0)

        path_to_json = self.path + "/" + execution_file
        with open(path_to_json, 'w') as outfile:
            json.dump(self.executions, outfile, indent=0)

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
    _dict = {}
    path_to_json = config_path + "/" + config_file
    if os.path.exists(path_to_json):
        with open(path_to_json) as f:
            _dict = json.load(f)

    _execs = {}
    path_to_execs = config_path + "/" + execution_file
    if os.path.exists(path_to_execs):
        with open(path_to_execs) as f:
            _execs['executions'] = json.load(f)

    _object = Projit(**_dict, **_execs )
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


