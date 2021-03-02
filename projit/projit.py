# -*- coding: utf-8 -*-

"""projit.projit: provides entry point main()."""

__version__ = "0.1.0"

import sys
import os

from .utils import locate_projit_config
from .config import config_folder

def main():
    if len(sys.argv) < 2:
        print("ERROR: MISSING ARGUMENTS")
        print_usage(sys.argv)
        exit(1)
    else:
        cmd = sys.argv[1]
        if cmd == "init":
            initialise_project(sys.argv)
        else:
            config_file = locate_projit_config() 
            print("CONFIG:", config_file)
            if config_file=="":
                print("This is not a projit project. Please use '>projit init'")
                exit(1)
            if cmd == "status":
                project_status(sys.argv)
            if cmd == "render":
                render_doc(sys.argv)


##########################################################################################        
def initialise_project(argv):
    print("YOU WANT TO INITIALISE")
    if len(argv) < 3:
        print("ERROR: Project initialistion requires parameter: <Project_Name>")
        exit(1)
    os.mkdir(config_folder)


##########################################################################################        
def project_status(argv):
    print("YOU WANT STATUS")

##########################################################################################        
def render_doc(argv):
    print("YOU WANT A DOC RENDERED")

##########################################################################################        
def print_usage(args):
    """ Command line application usage instrutions. """
    print("USAGE ")
    print(args[0], " <COMMAND> [<SUBCOMMAND>] [<PATH>]")
    print("  <COMMAND>    - Task to perform: init, status, run, render, clean")
    print("  <SUBCOMMAND> - (OPTIONAL) Dependant on task")
    print("  <PATH >      - (OPTIONAL) Dependant on task")
    print("")


##########################################################################################        
