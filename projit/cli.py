import argparse
import pandas as pd
import sys
import os

# -*- coding: utf-8 -*-
  
"""
   projit.cli: Command line interface for projit.
   This file provide argument parsing and execution via entry point main()
"""

from .utils import locate_projit_config
from .config import config_folder
from .utils import initialise_project
from .utils import get_properties
from .utils import write_properties
from .projit import load as projit_load
from .projit import init as projit_init

from projit import __version__

##########################################################################################
def task_init(name, template=''):
    """
    Initialise a project from the command line.
    This function request a description, and thus runs in interactive mode.
    """
    config_file = locate_projit_config()
    if config_file != "":
        print("ERROR: Projit Project already exists. Run `projit update` to change details.")
        exit(1)
#    print("Please enter a description for your project (or Press Enter to Cancel)")
#    descrip = input(">")
    descrip = ""
    if len(template)>9:
        if template[0:9]=="template=":
            template=template[9:]
    project = projit_init(template, name, descrip)


##########################################################################################
def task_update(project):
    """
    Update a project from the command line
    """
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
def task_status(project):
    print("")
    print("  Project: %s" % project.name)
    print("  Description: %s" % project.desc)
    print("  Datasets: %i" % len(project.datasets))
    print("  Experiments: %i" % len(project.experiments))
    print("")

##########################################################################################
def task_list(subcmd, project, dataset, markdown):
    """
    List content of a project from the command line
    """
    if subcmd == "datasets":
        print(" ___Datasets________________________________________")
        if len(project.datasets.keys()) > 0:
            long_key = max([len(k) for k in project.datasets.keys()])
            for ds in project.datasets:
                print(" ", ds, filler(len(ds), long_key+1 ), project.datasets[ds] )
        else:
            print(" NONE")
        print("")
    elif subcmd == "experiments":
        print(" ___Experiments_____________________________________")
        if len(project.experiments) > 0:
            long_key = max([len(k[0]) for k in project.experiments])
            for exp in project.experiments:
                print(" ", exp[0], filler(len(exp[0]), long_key+1 ), exp[1] )
        else:
            print(" NONE")
        print("")
    elif subcmd == "results":
        title = "Results"
        if dataset == "":
            rez = project.get_results()
        else:
            rez = project.get_results(dataset)
            title += " on [%s]"%dataset
        
        if markdown:
            print_results_markdown(title, rez)
        else:
            print(" ___Results__________________________________[ %s ]___" % dataset)
            pd.set_option('expand_frame_repr', False)
            pd.set_option('display.max_columns', 999)
            print(rez)

    else:
        print(" ERROR: List received an unrecognised sub-command: %s" % subcmd)
        exit(1)



##########################################################################################
def task_render(project, path):
    """
    Generates a pdf and writes it to the provided path
    """
    project.render(path)

##########################################################################################
def filler(current, max_len):
    return " " * (max_len - current)

##########################################################################################

def print_results_markdown(title, df):
    longest_name = max(df["experiment"].apply(lambda x: len(x)))
    name_spacer = 12
    if(longest_name>10):
        name_spacer = longest_name+2

    col_widths = [name_spacer]
    def colwidth(input):
         wid = len(input)
         if (wid<6):
             return 8
         return wid+2

    other_cols = list(df.columns)
    other_cols.remove("experiment")
    other_col_widths = list(map(colwidth, other_cols))


    def widthGenerator(col_names, col_widths):
        for colname, colwidth in zip(col_names, col_widths):
            longest =  max( df[colname].apply(lambda x: len(str(round(x,2)))))
            if longest > (colwidth-2):
                yield longest+2
            else:
                yield colwidth

    mygen = widthGenerator(other_cols, other_col_widths)
    other_col_widths = list(mygen)
    col_widths.extend(other_col_widths)
    total_widths = sum(col_widths)
    # This title line was an attempt to print it as a merged table cell
    # titleline = "| %s%s %s" % (title, " "*(total_widths-len(title)-2), "|"*(len(col_widths)) )
    titleline = "\n%s\n%s" % (title, "-"*len(title))
    print(titleline)
    header = ""
    for colname, colwidth in zip(list(df.columns), col_widths):
        header += ("| %s%s "% (colname, " "*(colwidth-len(colname)-2) ))
    header += "|"
    under = ""
    for colwith in col_widths:
        under += ("| %s:"% ( "-"*(colwith-2) ))
    under += "|"
    print(header)
    print(under)
    for i in range(len(df)):
        name = df.loc[i,"experiment"]
        rowcontent = "| %s%s "%(name, " "*(name_spacer-len(name)-2) )
        for colname, colwidth in zip(other_cols, other_col_widths):
            content = str(round(df.loc[i,colname],2))
            rowcontent += "| %s%s "%( " "*(colwidth-len(content)-2), content )
        rowcontent += "|"
        print(rowcontent)
    print("\n")

##########################################################################################
def task_add(project, asset, name, path):
    """
    Add elements to a project from the command line
    """
    if asset == "dataset":
        project.add_dataset(name, path)
    elif asset == "experiment":
        project.add_experiment(name, path)
    else:
        print("ERROR: Request to add unrecognised asset type: %s" % asset)
        exit(1)

##########################################################################################
def task_rm(project, asset, name):
    """
    Remove elements to a project from the command line
    """
    if asset not in ["dataset","experiment"]:
        print("ERROR: Request to remove unrecognised asset type: %s" % asset)
        exit(1)

    if name == ".":
        print(f"Remove all {asset}s. Please confirm (y/n)")
        response = input(">")
    else: 
        print(f"Remove {asset} named {name}. Please confirm (y/n)")
        response = input(">")

    if response=='y':
        if asset == "dataset":
            project.rm_dataset(name)
        if asset == "experiment":
            project.rm_experiment(name)
    else:
        print(f"** Remove command for {asset} named {name} cancelled ** ")

##########################################################################################
def print_usage(prog):
    """ Command line application usage instrutions. """
    print(" USAGE ")
    print(" ", prog, "[OPTIONS] <COMMAND> [<ASSET>] [<PARAMS>*]")
    print("   <COMMAND>     - CORE TASK TO PERFORM: [init | upate | rm | status | add | list | render]")
    print("   <ASSET>       - (OPTIONAL) Dependant on COMMAND: [dataset | experiment | results]")
    print("   <PARAMS>      - (OPTIONAL) Dependant on COMMAND: Usually names and paths")
    print("   [OPTIONS]")
    print("      -v, --version          - Print version")
    print("      -h, --help             - Get command help")
    print("      -m, --markdown         - Print out with markdown")
    print("")
    print("   COMMON USAGE PATTERNS")
    print("   ", prog, "init 'Project name'                     # Initialise project")
    print("   ", prog, "status                                  # View project status")
    print("   ", prog, "add dataset train data/train.csv        # Register training data")
    print("   ", prog, "add dataset test data/test.csv          # Register testing data")
    print("   ", prog, "add experiment explore explore.ipynb    # Register an experiment script")
    print("   ", prog, "list datasets                           # List the available datasets")
    print("   ", prog, "list experiments                        # List the registered experiments")
    print("   ", prog, "list results                            # List the registered results ")
    print("   ", prog, "-m list results test                    # List results on test data in markdown")
    print("   ", prog, "rm experiment explore                   # Remove the experiment explore (requires confirmation)")
    print("   ", prog, "rm experiment .                         # Remove all experiments (requires confirmation)")
    print("")



##########################################################################################
def main():
   parser = argparse.ArgumentParser()
   parser.add_argument('-v', '--version', help='Print Version', action='store_true')
   parser.add_argument('-m', '--markdown', help='Use markdown for output', action='store_true')

   subparsers = parser.add_subparsers(dest="cmd") 

   init_parser = subparsers.add_parser('init')
   init_parser.add_argument('name')
   init_parser.add_argument('template', nargs='?', default="")

   up_parser = subparsers.add_parser('update')

   add_parser = subparsers.add_parser('add')
   add_parser.add_argument('asset')
   add_parser.add_argument('name')
   add_parser.add_argument('path')

   list_parser = subparsers.add_parser('list')
   list_parser.add_argument('subcmd')
   list_parser.add_argument('dataset', nargs='?', default="")


   rm_parser = subparsers.add_parser('rm')
   rm_parser.add_argument('asset')
   rm_parser.add_argument('name')

   ren_parser = subparsers.add_parser('render')
   ren_parser.add_argument('path')

   sta_parser = subparsers.add_parser('status')
 
   args = parser.parse_args() 

   if args.version:
       print(" Version:", __version__)
       exit(1)

   if args.cmd == None:
       print_usage("projit")
       exit(1)

   if args.cmd == "init":
      task_init(args.name)
      exit(1)

   """
   From this point on all commands required that we are inside a valid projit project
   """
   config_path = locate_projit_config()
   if config_path=="":
       print(" ERROR: This is not a projit project.")
       print("        Please initialise the project first.")
       print(" > projit init <PROJECT NAME>")
       exit(1)

   project = projit_load(config_path)

   if args.cmd == 'list':
      task_list(args.subcmd, project, args.dataset, args.markdown)

   if args.cmd == 'add':
      task_add(project, args.asset, args.name, args.path)

   if args.cmd == 'rm':
      task_rm(project, args.asset, args.name)

   if args.cmd == 'update':
      task_update(project)

   if args.cmd == 'status':
      task_status(project)

   if args.cmd == 'render':
      task_render(project)


##########################################################################################
if __name__ == '__main__':
    main()
