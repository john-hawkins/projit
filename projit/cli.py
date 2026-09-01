# -*- coding: utf-8 -*-

"""
   projit.cli: Command line interface for projit.
   This file provides argument parsing and execution via the click-based CLI.
"""

import sys
import os

import click
import pandas as pd
import numpy as np

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

##################################################################################
def task_init(name, template=''):
    """
    CLI Internal Task Function: Initialise a project from the command line.
    This function will initate a project with a blank description.
    Users will need to update this in subsequent interation.

    :param name: The name of the project
    :type name: String, required

    :param template: The name of the template to use when initialising
    :type template: String, optional

    :return: None
    :rtype: None
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


##################################################################################
def task_update(project):
    """
    CLI Internal Task Function: Update a project from the command line

    This function invokes an interaction via the terminal to update
    the project properties.

    :return: None
    :rtype: None
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

##################################################################################
def task_status(project):
    """
    CLI Internal Task Function: Print the project properties to the command line

    :param project: The projit project object
    :type project: Projit, required

    :return: None
    :rtype: None
    """
    print("")
    print("  Project: %s" % project.name)
    print("  Description: %s" % project.desc)
    print("  Datasets: %i" % len(project.datasets))
    print("  Experiments: %i" % len(project.experiments))
    print("  Executions: %i" % project.get_total_executions())
    print("")

##################################################################################
def filler(current, max_len, content=" "):
    """
    Internal function to fill a string with spaces to max_len

    :param current: The length of the current content
    :type current: Int, required

    :param max_len: The maximum string length
    :type max_len: Int, required

    :param content: The character to fill with (default ' ')
    :type content: Char, optional

    :return: filled_content
    :rtype: String
    """
    return content * (max_len - current)

##################################################################################
def print_header(header):
    full_header = header + ("_" * (90-len(header)))
    print(full_header)

##################################################################################
def task_compare(project, datasets, metric, format, precision):
    """
    CLI Internal Task Function: Compare results across muliple datasets.

    This command loads the results for each dataset and extracts just the records
    for the specified metric to compile the comparison dataset to display.

    :param project: The projit project object
    :type project: Projit, required

    :param datasets: The list of datasets to compare
    :type datasets: list(String), required

    :param metric: The metric to use for comparison
    :type metric: String, required

    :param format: The output format (markdown|latex|default)
    :type format: String, required

    :param precision: The precision for results in the table 
    :type precision: Int, required

    :return: None
    :rtype: None
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

    results = results.round(precision)

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
    """
    CLI Internal Function: determine the maximum length of the content
    inside a specific set of tags on an asset in the project.
 
    :param project: The projit project object
    :type project: Projit, required

    :param asset: The asset type
    :type asset: String, required

    :param tags: The tags to search for
    :type tags: list(String), required
 
    :return: List of tag lengths
    :rtype: list(Int)
    """
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


################################################################################
def task_list(subcmd, project, dataset, format, precision, tags):
    """
    CLI Internal Task Function: List content of a project from the command line
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

        rez = rez.round(precision)
 
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



###############################################################################
def task_render(project, path):
    """
    Generates a pdf and writes it to the provided path

    :param project: The projit project object
    :type project: Projit, required

    :param path: The rendering path
    :type path: String, required
    """
    project.render(path)


###############################################################################

def print_results_latex(title, df):
    """
    Latex output - Putting this in a central function in case we change the 
    functionality or format in the future.

    :param title: The table title
    :type title: String, required

    :param df: The dataframe to print out
    :type df: DataFrame, required

    :return: None
    :rtype: None
    """
    #output = df.to_latex()
    #print(output)
    print_latex(df, title)

###############################################################################

def print_results_markdown(title, df):
    titleline = "\n%s\n%s" % (title, "-"*len(title))
    if df.empty or len(df["experiment"]) == 0:
        print(titleline)
        print()
        return
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

###############################################################################
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

################################################################################
def task_tag(project, asset, name, values):
    """
    Add tags to an asset in the project from the command line
    """
    vals = values.split(",")
    tags = {}
    for val in vals:
        if "=" not in val:
            print(f"ERROR: Invalid tag format '{val}'. Expected key=value pairs separated by commas.")
            exit(1)
        key, value = val.split("=", 1)
        if not key:
            print(f"ERROR: Empty tag key in '{val}'. Keys must be non-empty.")
            exit(1)
        tags[key] = value

    if project.validate_asset(asset, name):
        project.add_tags(asset, name, tags)
    else:
        print(f"ERROR: Invalid request to tag asset {name} of type {asset} - please check available assets")
        exit(1)


###############################################################################
def task_add_result(project, experiment, metric, value, dataset):
    """
    Record a result metric for an experiment from the command line
    """
    ds = dataset if dataset != "" else None
    try:
        project.add_result(experiment, metric, value, ds)
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)


###############################################################################
def task_start(project, name, path):
    """
    Start (register) an experiment execution from the command line
    """
    exec_id = project.start_experiment(name, path)
    print(exec_id)


###############################################################################
def task_stop(project, name, id):
    """
    End a previously started experiment execution from the command line
    """
    try:
        project.end_experiment(name, id)
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)


###############################################################################
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

###############################################################################
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


#################################################################################
# Click CLI
#################################################################################

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group(context_settings=CONTEXT_SETTINGS, invoke_without_command=True)
@click.version_option(__version__, "-v", "--version")
@click.option("-m", "--markdown", is_flag=True, default=False,
              help="Use markdown format for results output.")
@click.option("-l", "--latex", is_flag=True, default=False,
              help="Use LaTeX format for results output (overrides -m).")
@click.option("-p", "--precision", type=int, default=3, show_default=True,
              help="Numerical precision for displayed results.")
@click.pass_context
def cli(ctx, markdown, latex, precision):
    """projit — project tracking for data science and ML experiments.

    Run 'projit COMMAND --help' for detailed help on any subcommand.

    \b
    Common usage patterns:
      projit init 'Project name'                     # Initialise project
      projit status                                  # View project status
      projit add dataset train data/train.csv        # Register training data
      projit add experiment explore explore.ipynb    # Register an experiment
      projit start explore explore.ipynb             # Register an execution start
      projit stop explore <execution id>             # Close out that execution
      projit add-result explore rmse 12.4            # Record a result metric
      projit list datasets                           # List datasets
      projit list experiments                        # List experiments
      projit list results                            # List all results
      projit list results test                       # Results for dataset 'test'
      projit -m list results test                    # Results in Markdown format
      projit compare dataone,datatwo MAE             # Compare results by metric
      projit render path_to_output.pdf               # Render PDF summary
    """
    ctx.ensure_object(dict)
    ctx.obj["format"] = "latex" if latex else ("markdown" if markdown else "simple")
    ctx.obj["precision"] = precision
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


def _require_project():
    """Load and return the current project, or exit with an error."""
    config_path = locate_projit_config()
    if config_path == "":
        click.echo(" ERROR: This is not a projit project.")
        click.echo("        Please initialise the project first.")
        click.echo(" > projit init <PROJECT NAME>")
        raise SystemExit(1)
    return projit_load(config_path)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.argument("template", default="")
def init(name, template):
    """Initialise a new projit project in the current directory.

    NAME is the project name.
    TEMPLATE (optional) is the project template to use (default: 'default').
    """
    task_init(name, template)


@cli.command(context_settings=CONTEXT_SETTINGS)
def update():
    """Interactively update the project name and description."""
    project = _require_project()
    task_update(project)


@cli.command(context_settings=CONTEXT_SETTINGS)
def status():
    """Show a summary of the current project (datasets, experiments, runs)."""
    project = _require_project()
    task_status(project)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("asset", type=click.Choice(["dataset", "experiment"]))
@click.argument("name")
@click.argument("path")
def add(asset, name, path):
    """Register a dataset or experiment with the project.

    \b
    ASSET  the type to register: 'dataset' or 'experiment'
    NAME   the label used to refer to this asset
    PATH   the file system path (or URL) to the asset
    """
    project = _require_project()
    task_add(project, asset, name, path)


@cli.command(name="add-result", context_settings=CONTEXT_SETTINGS)
@click.argument("experiment")
@click.argument("metric")
@click.argument("value", type=float)
@click.argument("dataset", default="")
def add_result(experiment, metric, value, dataset):
    """Record a result metric for an experiment.

    \b
    EXPERIMENT  the experiment name (must already be registered)
    METRIC      the metric name, e.g. 'rmse'
    VALUE       the numeric metric value
    DATASET     (optional) associate the result with a specific registered dataset
    """
    project = _require_project()
    task_add_result(project, experiment, metric, value, dataset)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.argument("path")
def start(name, path):
    """Start (register) an execution of an experiment and print its execution ID.

    \b
    NAME  the experiment name
    PATH  the path to the experiment script

    Registers the experiment if it isn't already, and prints the execution
    ID, which must be passed to 'projit stop' to close out this execution
    record. Run your experiment script yourself between 'projit start' and
    'projit stop' -- projit does not execute it for you.
    """
    project = _require_project()
    task_start(project, name, path)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("name")
@click.argument("id")
def stop(name, id):
    """End a previously started experiment execution.

    \b
    NAME  the experiment name
    ID    the execution ID printed by 'projit start'
    """
    project = _require_project()
    task_stop(project, name, id)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("asset", type=click.Choice(["dataset", "experiment"]))
@click.argument("name")
@click.argument("values")
def tag(asset, name, values):
    """Add key=value metadata tags to a dataset or experiment.

    \b
    ASSET   the asset type: 'dataset' or 'experiment'
    NAME    the name of the asset to tag
    VALUES  comma-separated key=value pairs, e.g. 'env=prod,split=80'
    """
    project = _require_project()
    task_tag(project, asset, name, values)


@cli.command(name="list", context_settings=CONTEXT_SETTINGS)
@click.argument("subcmd", type=click.Choice(["datasets", "experiments", "results"]))
@click.argument("dataset", default="")
@click.option("--tags", multiple=True,
              help="Tag columns to include in the output (repeatable).")
@click.pass_context
def list_cmd(ctx, subcmd, dataset, tags):
    """List datasets, experiments, or results registered in this project.

    \b
    SUBCMD   what to list: 'datasets', 'experiments', or 'results'
    DATASET  (optional) filter results to a specific dataset name

    Supports the global -m/--markdown, -l/--latex, and -p/--precision options.
    """
    project = _require_project()
    fmt = ctx.obj.get("format", "simple")
    precision = ctx.obj.get("precision", 3)
    task_list(subcmd, project, dataset, fmt, precision, list(tags))


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("asset", type=click.Choice(["dataset", "experiment"]))
@click.argument("name")
def rm(asset, name):
    """Remove a dataset or experiment from the project (requires confirmation).

    \b
    ASSET  the asset type: 'dataset' or 'experiment'
    NAME   the name of the asset to remove; use '.' to remove all of that type
    """
    project = _require_project()
    task_rm(project, asset, name)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("datasets")
@click.argument("metric")
@click.pass_context
def compare(ctx, datasets, metric):
    """Compare experiment results across multiple datasets for a given metric.

    \b
    DATASETS  comma-separated list of dataset names, e.g. 'train,test,val'
    METRIC    the result column to compare across datasets

    Supports the global -m/--markdown, -l/--latex, and -p/--precision options.
    """
    project = _require_project()
    fmt = ctx.obj.get("format", "simple")
    precision = ctx.obj.get("precision", 3)
    dataset_list = datasets.split(",")
    task_compare(project, dataset_list, metric, fmt, precision)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("experiment")
@click.argument("property", type=click.Choice(["execution", "hyperparam", "result"]))
@click.argument("metric", default="")
def plot(experiment, property, metric):
    """Plot execution times or tracked values for an experiment.

    \b
    EXPERIMENT  the name of the experiment to plot
    PROPERTY    what to plot: 'execution', 'hyperparam', or 'result'
    METRIC      required when PROPERTY is 'hyperparam' or 'result'
    """
    project = _require_project()
    task_plot(project, experiment, property, metric)


@cli.command(context_settings=CONTEXT_SETTINGS)
@click.argument("path")
def render(path):
    """Render a PDF summary document for the project.

    PATH is the output file path, e.g. 'reports/summary.pdf'.
    """
    project = _require_project()
    task_render(project, path)


#################################################################################
# Entrypoint
#################################################################################

def main():
    cli()


# Backward-compatibility alias used by existing tests that import cli_main
cli_main = cli


#################################################################################
if __name__ == "__main__":
    main()
