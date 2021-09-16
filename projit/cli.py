# -*- coding: utf-8 -*-

"""projit.cli: provides entry point main()."""
import pandas as pd
import sys
import os

from .utils import locate_projit_config
from .config import config_folder
from .utils import initialise_project
from .utils import get_properties
from .utils import write_properties
from .projit import load as projit_load
from .projit import init as projit_init

from projit import __version__
 
def main():
    if len(sys.argv) < 2:
        print("ERROR: MISSING ARGUMENTS")
        print_usage(sys.argv)
        exit(1)
    else:
        cmd = sys.argv[1]
        if len(sys.argv) == 2:
            if sys.argv[1] in ["-v", "--version"]:
                print(" Version:", __version__)
                exit(1)
            elif sys.argv[1] in ["-h", "--help"]:
                print_usage(sys.argv)
                exit(1)
        
        if cmd == "init":
            init(sys.argv)
            exit(1)

        config_path = locate_projit_config() 
        if config_path=="":
            print(" ERROR: This is not a projit project.")
            print("        Please initialise the project first.")
            print(" > projit init <PROJECT NAME>")
            exit(1)

        project = projit_load(config_path)

        if cmd == "update":
            update(project)
            exit(1)
        if cmd == "status":
            project_status(project)
            exit(1)
        if cmd == "render":
            if len(sys.argv) < 3:
                print(" ERROR: Rendering a project requires a path for output file.")
                exit(1)
            else:
                path = sys.argv[2]
                render_doc(project, path)
                exit(1)
        if cmd == "list":
            if len(sys.argv) < 3:
                print(" ERROR: MISSING ARGUMENTS")
                print_usage(sys.argv)
                exit(1)
            else:
                subcmd = sys.argv[2]
                printlist(subcmd, project, sys.argv)
                exit(1)
        if cmd == "add":
            if len(sys.argv) < 5:
                print(" ERROR: MISSING ARGUMENTS")
                print_usage(sys.argv)
                exit(1)
            else:
                subcmd = sys.argv[2]
                add(subcmd, project, sys.argv)
                exit(1)

        print(" ERROR: UNKNOWN ARGUMENTS")
        print_usage(sys.argv)

##########################################################################################        
def init(argv):
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
def render_doc(project, path):
    project.render(path)
 
##########################################################################################        
def printlist(subcmd, project, argv):
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
    elif subcmd == "results":
        dataset = "*"
        title = "Results"
        if len(argv)>3:
            dataset = argv[3]
            rez = project.get_results(dataset)
            title += " on [%s]"%dataset
        else:
            rez = project.get_results()
        #print(" ___Results__________________________________[ %s ]___" % dataset)
        #pd.set_option('expand_frame_repr', False)
        #pd.set_option('display.max_columns', 999)
        print_results_markdown(title, rez)
    else:
        print("ERROR: Unrecognised SUBCOMMAND: %s" % subcmd)
        exit(1)

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
    print(" USAGE ")
    print(" ", args[0], " [OPTIONS] <COMMAND> [<SUBCOMMAND>] [<PARAMS>*]")
    print("   <COMMAND>     - CORE TASK TO PERFORM: [init | upate | status | add | list | render]")
    print("   <SUBCOMMAND>  - (OPTIONAL) Dependant on COMMAND: [dataset | experiment | results]")
    print("   <PARAMS>      - (OPTIONAL) Dependant on COMMAND: Usually names and paths")
    print("   [OPTIONS]")
    print("      -v             - Print version")
    print("      -h             - Print this usage help")
    print("")
    print("   COMMON PATTERNS")
    print("   ", args[0], "init 'Project name'")
    print("   ", args[0], "status")
    print("   ", args[0], "add dataset train data/train.csv")
    print("   ", args[0], "add dataset test data/test.csv")
    print("   ", args[0], "add experiment exploration exp/explore.ipynb")
    print("   ", args[0], "list datasets")
    print("   ", args[0], "list experiments")
    print("   ", args[0], "list results")
    print("")

##########################################################################################        
