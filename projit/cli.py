import argparse
import pandas as pd
import numpy as np
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
from .ascii_plot import ascii_plot
from .latex_table import print_latex

from projit import __version__

project = None

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
    if name == "":
        name = project.name
    if descrip == "":
        descrip = project.desc
    project.update_name_description(name, descrip)

##########################################################################################
def task_status(project):
    print("")
    print("  Project: %s" % project.name)
    print("  Description: %s" % project.desc)
    print("  Datasets: %i" % len(project.datasets))
    print("  Experiments: %i" % len(project.experiments))
    print("  Executions: %i" % len(project.executions))
    print("")

##########################################################################################
def filler(current, max_len, content=" "):
    return content * (max_len - current)

##########################################################################################
def print_header(header):
    full_header = header + ("_" * (90-len(header)))
    print(full_header)

##########################################################################################
def task_compare(project, datasets, metric, format):
   """
   Compare results across muliple datasets.
   This command loads the results for each dataset and extarcts just the records
   for the specified metric to compile the comparison dataset to display.
   """
   title = "Compare Results" 
   warning = ""
   results = None
   for dataset in datasets: 
       rez = project.get_results(dataset)
       if metric not in rez.columns:
           rez[metric] = np.nan
           warning += f"Metric '{metric}' not present for dataset '{dataset}'\n"
       rez = rez.loc[:,['experiment',metric]]
       rez.columns = ['experiment', dataset]
       if results is None:
           results = rez
       else:
           results = pd.merge(results,rez,on="experiment")
           
   if len(warning) > 0:
       print("*** WARNINGS ***")
       print(warning)

   if format == 'markdown':
        print_results_markdown(title, results)
   elif format == 'latex':
        print_results_latex(title, results)
   else:
        print(" ___" + title + "__________________________________[ %s ]___" % metric)
        pd.set_option('expand_frame_repr', False)
        pd.set_option('display.max_columns', 999)
        print(results)


def extract_max_tags_lengths(project, asset, tags):
    if asset in project.tags:
        tagset = project.tags[asset]
        max_tag_lengths = []
        for t in tags:
            temp = []
            for a in tagset:
                if t in tagset[a]:
                    temp.append(len(tagset[a][t]))
                else:
                    temp.append(0)
            max_val = max(temp)
            if max_val<len(t):
               max_val = len(t)
            max_tag_lengths.append(max_val)
        return max_tag_lengths
    else:
        return [0 for x in tags]


##########################################################################################
def task_list(subcmd, project, dataset, format, tags):
    """
    List content of a project from the command line
    """
    if len(tags) > 0:
        tags_max_len = max([len(x) for x in tags])
    else:
        tags = []
        tags_max_len = 0

    print()
    if subcmd == "datasets":
        print_header("__Datasets")
        if len(project.datasets.keys()) > 0:
            tag_header = ""
            if len(tags)>0:
               tag_max_lengths = extract_max_tags_lengths(project, "dataset", tags)
               for tag,tag_len in zip(tags,tag_max_lengths):
                   tag_header = tag_header + tag + filler(len(tag), tag_len+3, "_")
                
            long_key = max([len(k) for k in project.datasets.keys()])
            myhead = "__Name" + filler(len("Name"), long_key+3, "_") + tag_header + "Path_________"
            print_header(myhead)
            for ds in project.datasets:
                tag_output = ""
                if len(tags)>0:
                    tag_vals = project.get_tags("dataset", ds, tags)                
                    for tag,tag_len in zip(tag_vals,tag_max_lengths):
                        tag_output = tag_output + tag + filler(len(tag), tag_len+3, " ")
                print("  ", ds, filler(len(ds), long_key+3 ), tag_output, project.datasets[ds], sep="" )
        else:
            print(" NONE")
        print("")
    elif subcmd == "experiments":
        print_header("__Experiments")
        if len(project.experiments) > 0:
            tag_header = ""
            if len(tags)>0:
               tag_max_lengths = extract_max_tags_lengths(project, "experiment", tags)
               for tag,tag_len in zip(tags,tag_max_lengths):
                   tag_header = tag_header + tag + filler(len(tag), tag_len+3, "_")

            long_key = max([len(k[0]) for k in project.experiments])
            myhead = "__Name__" + filler(len("Name__"), long_key+3, "_") + tag_header + "Runs__" + "MeanRunTime___" + "Path______"
            print_header(myhead)
            for exp in project.experiments:
                tag_output = ""
                if len(tags)>0:
                    tag_vals = project.get_tags("experiment", exp[0], tags)
                    for tag,tag_len in zip(tag_vals,tag_max_lengths):
                        tag_output = tag_output + tag + filler(len(tag), tag_len+3, " ")
                execs, mean_time = project.get_experiment_execution_stats(exp[0])
                mins, secs = divmod(mean_time, 60)
                if mins>60:
                    hours, mins = divmod(mins, 60)
                else:
                    hours = 0
                hours = int(hours)
                mins = int(mins)
                secs = int(secs)
                if hours>9:
                    h_str = f"{hours}h"
                elif hours==0:
                    h_str = f"   "
                else:
                    h_str = f" {hours}h"

                if mins>9:
                    m_str = f"{mins}m"
                elif mins==0:
                    m_str = f"   "
                else:
                    m_str = f" {mins}m"

                if secs>9:
                    s_str = f"{secs}s"
                elif mins==0:
                    s_str = f"   "
                else:
                    s_str = f" {secs}s"

                mytime = f" {h_str} {m_str} {s_str}  "

                print("  ", exp[0], filler(len(exp[0]), long_key+3), tag_output, 
                           filler(len(str(execs)), 4), execs, "  ", 
                           mytime, filler(len(str(mytime)), 12), 
                           exp[1], sep=""  
                )
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
 
        if format == 'markdown':
            print_results_markdown(title, rez)
        elif format == 'latex':
            print_results_latex(title, rez)
        else:
            print_header(f"__Results__[{dataset}]")
            pd.set_option('expand_frame_repr', False)
            pd.set_option('display.max_columns', 999)
            print(rez)
            print()
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

def print_results_latex(title, df):
    """
    Latex output - Putting this in a central function in case we change the functionality
     or format in the future.
    """
    #output = df.to_latex()
    #print(output)
    print_latex(df, title)

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
    print()

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
def task_tag(project, asset, name, values):
    """
    Add tags to an asset in the project from the command line
    """
    vals = values.split(",")
    tags = {}
    for val in vals:
        temp = val.split("=")
        tags[temp[0]] = temp[1]

    if project.validate_asset(asset, name):
        project.add_tags(asset, name, tags)
    else: 
        print(f"ERROR: Invalid request to tag asset {name} of type {asset} - please check available assets")
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
def task_plot(project, experiment, property, metric):
    if property == "execution":
        print()
        print_header(f"__Experiment_[{experiment}]_execution_time_")
        values = project.get_execution_times(experiment)
        print(ascii_plot(values, xlabel='Iteration', ylabel='Seconds',  width=70, height=12)) 
        print()
    elif property == "hyperparam":
        print()
        print_header(f"__Experiment_[{experiment}]_hyperparameter_[{metric}]_")
        print("  TODO")
        print()
        #print(ascii_plot([50,90,130,70,60,0,80,120,100], xlabel='Iteration', ylabel=metric, width=70, height=12)) 
    elif property == "result":
        print()
        print_header(f"__Experiment_[{experiment}]_result_[{metric}]_")
        print("  TODO")
        print()
        #print(ascii_plot([50,90,130,70,60,0,80,120,100], xlabel='Iteration', ylabel=metric, width=70, height=12)) 
    else:
        print()
        print(f"\nUnrecognized Experiment Property [{property}] -- Valid Options [execution,hyperparam,result]")
        print()


##########################################################################################
def print_usage(prog):
    """ Command line application usage instrutions. """
    print(" USAGE ")
    print(" ", prog, "[OPTIONS] <COMMAND> [<ASSET>] [<PARAMS>*]")
    print("   <COMMAND>     - CORE TASK TO PERFORM: [init | upate | rm | status | add | list | compare | render]")
    print("   <ASSET>       - (OPTIONAL) Dependant on COMMAND: [dataset | experiment | results]")
    print("   <PARAMS>      - (OPTIONAL) Dependant on COMMAND: Usually names and paths")
    print("   [OPTIONS]")
    print("      -v, --version          - Print version")
    print("      -h, --help             - Get command help")
    print("      -m, --markdown         - Use markdown format when printing results")
    print("      -l, --latex            - Use LaTeX format when printing results")
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
    print("   ", prog, "list results test                       # List the registered results on dataset 'test' ")
    print("   ", prog, "plot initial execution                  # Plot the execution times for the experiment named 'initial'")
    print("   ", prog, "plot initial hyperparam alpha           # Plot the change in hyperparam 'alpha' for the experiment named 'initial'")
    print("   ", prog, "plot initial result MSE                 # Plot the change in result 'MSE' for the experiment named 'initial'")
    print("   ", prog, "render path_to_output.pdf               # Render a PDF document summarising the project")
    print("   ", prog, "-m list results test                    # List results on 'test' data in Markdown format")
    print("   ", prog, "rm experiment explore                   # Remove the experiment explore (requires confirmation)")
    print("   ", prog, "rm experiment .                         # Remove all experiments (requires confirmation)")
    print("   ", prog, "-m list results test                    # List results on test data in Markdown format")
    print("   ", prog, "compare dataone,datatwo MAE             # Compare results over datasets using metric MAE")
    print("")


##########################################################################################
def main():
    try:
        cli_main()
    except Exception as e:
        print("*** Projit CLI Error ***")
        print(e)
    finally:
        if project is not None:
            project.release_lock()


##########################################################################################
def cli_main():
   parser = argparse.ArgumentParser()
   parser.add_argument('-v', '--version', help='Print Version', action='store_true')
   parser.add_argument('-m', '--markdown', help='Use markdown for output', action='store_true')
   parser.add_argument('-l', '--latex', help='Use LaTeX for output - overrides markdown', action='store_true')
   parser.add_argument('-u', '--usage', help='Print detailed usage instructions with examples', action='store_true')

   subparsers = parser.add_subparsers(dest="cmd") 

   init_parser = subparsers.add_parser('init')
   init_parser.add_argument('name')
   init_parser.add_argument('template', nargs='?', default="")

   up_parser = subparsers.add_parser('update')

   add_parser = subparsers.add_parser('add')
   add_parser.add_argument('asset')
   add_parser.add_argument('name')
   add_parser.add_argument('path')

   add_parser = subparsers.add_parser('tag')
   add_parser.add_argument('asset')
   add_parser.add_argument('name')
   add_parser.add_argument('values')

   list_parser = subparsers.add_parser('list')
   list_parser.add_argument('subcmd')
   list_parser.add_argument('dataset', nargs='?', default="")
   list_parser.add_argument('--tags', nargs='+', default="")

   plot_parser = subparsers.add_parser('plot')
   plot_parser.add_argument('experiment')
   plot_parser.add_argument('property')
   plot_parser.add_argument('metric', nargs='?', default="")

   rm_parser = subparsers.add_parser('rm')
   rm_parser.add_argument('asset')
   rm_parser.add_argument('name')

   comp_parser = subparsers.add_parser('compare')
   comp_parser.add_argument('datasets')
   comp_parser.add_argument('metric')

   ren_parser = subparsers.add_parser('render')
   ren_parser.add_argument('path')

   sta_parser = subparsers.add_parser('status')
 
   args = parser.parse_args() 

   if args.version:
       print(" Version:", __version__)
       exit(1)

   if args.usage:
       print_usage("projit")
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

   format = 'simple'
   if args.markdown:
       format = 'markdown'
   if args.latex:
       format = 'latex'

   if args.cmd == 'list':
      task_list(args.subcmd, project, args.dataset, format, args.tags)

   if args.cmd == 'compare':
      datasets = args.datasets.split(",")
      task_compare(project, datasets, args.metric, format)

   if args.cmd == 'add':
      task_add(project, args.asset, args.name, args.path)

   if args.cmd == 'tag':
      task_tag(project, args.asset, args.name, args.values)

   if args.cmd == 'rm':
      task_rm(project, args.asset, args.name)

   if args.cmd == 'plot':
      task_plot(project, args.experiment, args.property, args.metric)

   if args.cmd == 'update':
      task_update(project)

   if args.cmd == 'status':
      task_status(project)

   if args.cmd == 'render':
      task_render(project, args.path)


##########################################################################################
if __name__ == '__main__':
    main()
