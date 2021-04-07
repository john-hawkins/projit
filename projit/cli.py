# -*- coding: utf-8 -*-

"""projit.cli: provides entry point main()."""

__version__ = "0.1.0"

import sys
import os

from .utils import locate_projit_config
from .config import config_folder
from .utils import initialise_project
from .utils import get_properties
from .utils import write_properties
import projit as proj
 
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
            print("CONFIG:", config_path)
            if config_path=="":
                print("This is not a projit project. Please use '>projit init <Project_Name>'")
                exit(1)

            project = proj.load(config_path)

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
                    list(subcmd, config_path)


##########################################################################################        
def init(argv):
    print("YOU WANT TO INITIALISE")
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
        initialise_project(argv[2], descrip)
    else:
        print("Cancelling...")
        exit(0)

##########################################################################################       
def update(config_path):
    cfg = get_properties(config_path)
    print("Current Project Name: ", cfg['project_name'])
    print("Enter an alternative project name (or press enter to keep)")
    name = input(">")
    print("Current Description: ", cfg['description'])
    print("Enter an alternative description (or press enter to keep)")
    descrip = input(">")
    if name != "":
        cfg['project_name'] = name
    if descrip != "":
        cfg['description'] = descrip
    write_properties(config_path, cfg)


##########################################################################################        
def project_status(project):
    print(" > Project: %s" % project.name)
    print(" > Datasets: %s" % project.name)
    print(" > Experiments: %s" % project.name)

##########################################################################################        
def render_doc(project):
    print("YOU WANT A DOC RENDERED")
 
##########################################################################################        
def list(subcmd, project):
    print("LISTING")

##########################################################################################        
def print_usage(args):
    """ Command line application usage instrutions. """
    print("USAGE ")
    print(args[0], " <COMMAND> [<SUBCOMMAND>] [<PARAMS>*]")
    print("  <COMMAND>     - Core Task: init, status, list, add, run, render")
    print("  <SUBCOMMAND>  - (OPTIONAL) Dependant on task")
    print("  <PARAMS>      - (OPTIONAL) Dependant on task")
    print("")


##########################################################################################        
