# -*- coding: utf-8 -*-

"""projit.cli: provides entry point main()."""

import sys
import os

from .utils import locate_projit_config
from .config import config_folder
from .utils import initialise_project
from .utils import get_properties
from .utils import write_properties
from .projit import load as projit_load
from .projit import init as projit_init
 
def main():
    if len(sys.argv) < 2:
        print("ERROR: MISSING ARGUMENTS")
        print_usage(sys.argv)
        exit(1)
    else:
        cmd = sys.argv[1]
        if cmd == "init":
            init(sys.argv)
        else:
            config_path = locate_projit_config() 
            #print("CONFIG:", config_path)
            if config_path=="":
                print("This is not a projit project. Please use '>projit init <Project_Name>'")
                exit(1)

            project = projit_load(config_path)

            if cmd == "update":
                update(project)
            if cmd == "status":
                project_status(project)
            if cmd == "render":
                render_doc(project)
            if cmd == "list":
                if len(sys.argv) < 2:
                    print("ERROR: MISSING ARGUMENTS")
                    print_usage(sys.argv)
                    exit(1)
                else:
                    subcmd = sys.argv[2]
                    list(subcmd, project)
            if cmd == "add":
                if len(sys.argv) < 2:
                    print("ERROR: MISSING ARGUMENTS")
                    print_usage(sys.argv)
                    exit(1)
                else:
                    subcmd = sys.argv[2]
                    add(subcmd, project, sys.argv)


##########################################################################################        
def init(argv):
    #print("YOU WANT TO INITIALISE")
    config_file = locate_projit_config()
    if config_file != "":
        print("ERROR: Project exists. Run `projit update` to change details ")
        exit(1)
    if len(argv) < 3:
        print("ERROR: Project initialisation requires parameter: <Project_Name>")
        exit(1)
    print("Please enter a description for your project (or Press Enter to Cancel)")
    descrip = input(">")
    if len(descrip) > 0:
        if len(argv)>3:
            template=argv[3]
            if len(template)>9:
                if template[0:9]=="template=":
                    template=template[9:]
        else:
            template=''
        project = projit_init(template, argv[2], descrip)
    else:
        print("Cancelling...")
        exit(0)

##########################################################################################       
def update(project):
    print("Current Project Name: ", project.name)
    print("Enter an alternative project name (or press enter to keep)")
    name = input(">")
    print("Current Description: ", project.desc)
    print("Enter an alternative description (or press enter to keep)")
    descrip = input(">")
    if name != "":
        project.name = name
    if descrip != "":
        project.desc = descrip
    project.save()


##########################################################################################        
def project_status(project):
    print("")
    print("  Project: %s" % project.name)
    print("  Description: %s" % project.desc)
    print("  Datasets: %i" % len(project.datasets))
    print("  Experiments: %i" % len(project.experiments))
    print("")

##########################################################################################        
def render_doc(project):
    print("YOU WANT A DOC RENDERED")
 
##########################################################################################        
def list(subcmd, project):
    if subcmd == "datasets":
        long_key = max([len(k) for k in project.datasets.keys()])
        print(" ___Datasets________________________________________")
        for ds in project.datasets:
            print(" ", ds, filler(len(ds), long_key+1 ), project.datasets[ds] )
        print("")
    elif subcmd == "experiments":
        print(" ___Experiments_____________________________________")
        long_key = max([len(k[0]) for k in project.experiments])
        for exp in project.experiments:
            print(" ", exp[0], filler(len(exp[0]), long_key+1 ), exp[1] )
        print("")
    else:
        print("ERROR: Unrecognised SUBCOMMAND: %s" % subcmd)
        exit(1)

def filler(current, max_len):
    return " " * (max_len - current) 

##########################################################################################        
def add(subcmd, project, args):
    if subcmd == "dataset":
        name = args[3]
        path = args[4]
        project.add_dataset(name, path)
    elif subcmd == "experiment":
        name = args[3]
        path = args[4]
        project.add_experiment(name, path)
    else:
        print("ERROR: Unrecognised SUBCOMMAND: %s" % subcmd)
        exit(1)


##########################################################################################        
def print_usage(args):
    """ Command line application usage instrutions. """
    print("USAGE ")
    print(args[0], " <COMMAND> [<SUBCOMMAND>] [<PARAMS>*]")
    print("  <COMMAND>     - Core Task: init, status, list, add, run, render")
    print("  <SUBCOMMAND>  - (OPTIONAL) Dependant on COMMAND: dataset, experiment")
    print("  <PARAMS>      - (OPTIONAL) Dependant on task, names and paths")
    print("")
    print("COMMON PATTERN")
    print(args[0], "init 'Project name'")
    print(args[0], "status")
    print(args[0], "add dataset train data/train.csv")
    print(args[0], "add dataset test data/test.csv")
    print(args[0], "add experiment exploration exp/explore.ipynb")
    print(args[0], "lists datasets")
    print("")


##########################################################################################        
