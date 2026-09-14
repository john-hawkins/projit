Usage Guide
===========

Usage of projit happens at multiple points in a project development.

This page is a topic-by-topic reference and mixes CLI and API examples
within each section. If you'd rather see one complete project lifecycle
worked through end-to-end using only one interface, see
:doc:`tutorial_cli` (CLI-only) or :doc:`tutorial_api` (API-only).

Project Initialization
^^^^^^^^^^^^^^^^^^^^^^

Initialise a project as follows

.. code-block:: bash

    >projit init <Project-Name>

This command will create the projit configuration folder then write the project properties file.

If you would like the initialisation process to create a set of directories you can add an 
additional parameter for the template to use.
For example:

.. code-block:: bash

    >projit init <Project-Name> template=default

OR

.. code-block:: bash

    >projit init <Project-Name> template=cookiecutter-data-science

Each of these two commands will read the template definitions inside the
```templates``` directory and create all the specified directories.

The ``template=`` prefix shown above is optional and kept only for backward
compatibility -- ``projit init <Project-Name> default`` (without the
``template=`` prefix) works identically, and is what ``projit init --help``
shows.

You can then update these properties as follows:

.. code-block:: bash

    >projit update

This will show you the current values and prompt for an update


Manage Data Sets
^^^^^^^^^^^^^^^^^^^^

Add a data set with the following command:

.. code-block:: bash

    >projit add dataset train data/train.csv

You can then access the dataset inside a python script using the projit
package and the following syntax:

.. code-block:: python 

    import projit as pit
    project = pit.projit_load()
    train_data = project.get_dataset("train")

You can list all registered datasets by reading the ``datasets`` attribute
directly -- it is a plain dictionary of ``{name: path}`` and there is no
separate ``list_datasets()`` API method:

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    for name, path in project.datasets.items():
        print(name, path)

Note that the following syntax will work regardless of where in the directory structure the
script is extected. The projit Project determines the path to the data with the condition that
when you record the data it must be given a path relative to the root directory of the project.

You can modify a dataset by simply adding it again. This will overwrite any previous path.

You can remove a dataset with the 'rm' command

.. code-block:: bash

    >projit rm dataset train

You can also remove all datasets use the '.' wildcard:


.. code-block:: bash

    >projit rm dataset .


Manage Experiments
^^^^^^^^^^^^^^^^^^^^^

You can add experiments using the CLI

.. code-block:: bash

    >projit add experiment "Initial Exp" experiments/exp_one.py

This can also be done inside the experiment script itself:

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    project.add_experiment("Initial Exp", "experiments/exp_one.py")


.. note::
    The path to the experiment should be relative to the root directory.
    TODO: Automate the resolution of these paths.

You can modify an experiment by simply adding it again. This will overwrite any previous path.

You can remove an experiment with the 'rm' command

.. code-block:: bash

    >projit rm experiment "Initial Exp"

You can also remove all experiments use the '.' wildcard:

.. code-block:: bash

    >projit rm experiment .


You can alternatively manage experiments through the start and end functions.
These enable you to track executions of your project over time, including
the time elapsed in execution, different parameters and hyperparameters used
over each iteration.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    exec_id = project.start_experiment("Initial Exp", "experiments/exp_one.py", params={})
    #
    # INSERT ALL EXPERIMENT CODE HERE
    #
    project.end_experiment("Initial Exp", exec_id, hyperparams={})

This will add the experiment if it is not already registered.
It will then create an execution record for the first and all subsequent
executions of the script. The execution record will contain start and end times,
the git hash (if present) of the codebase
and any optional parameters or hyperparameters you wish to record.

.. important::
    ``start_experiment``/``end_experiment`` do not run your script for you --
    they only bracket a timestamped metadata record around code that you run
    yourself between the two calls. Neither ``params`` nor ``hyperparams`` is
    read by projit or passed into your script; they are opaque dictionaries
    stored on the execution record for your own later reference. By
    convention, ``params`` (passed to ``start_experiment``) records
    configuration known *before* the run -- e.g. dataset split, random seed,
    target column -- while ``hyperparams`` (passed to ``end_experiment``)
    records values decided or finalised *during or after* the run. Nothing
    enforces this split: if you want the values in ``params`` to actually
    configure your run, your own code must read them back out of the dict
    you passed in.

The same start/end pattern is available from the CLI, for wrapping a script
you run yourself without writing any Python:

.. code-block:: bash

    EXEC_ID=$(projit start "Initial Exp" experiments/exp_one.py)
    python experiments/exp_one.py
    projit stop "Initial Exp" "$EXEC_ID"

``projit start`` prints the execution ID to stdout, which must be captured
and passed to ``projit stop`` to close out that execution record. As with
the Python API, ``projit start`` registers the experiment automatically if
it isn't already registered. The CLI versions don't currently accept
``params``/``hyperparams`` -- use the Python API if you need to record
those.


You can list the experiments you have registered and executed using the CLI:

.. code-block:: bash

    >projit list experiments

    __Experiments___________________________________________________________________
    __Name_____________Runs__MeanTime____Path_______________________________________
      Initial Exp      4     42s         experiments/exp_one.py
      Second Exp       2     19s         experiments/exp_two.py


This will produce a table that includes a count of the executions and the mean execution time.

You can also produce a simple ascii plot of the execution time over all iterations of a particular experiment.

.. code-block:: bash

    >projit plot "Initial Exp" execution

    __Experiment_[Initial Exp]_execution_time____________________________________
    Seconds
    84.0   +
           |                                                                       
           |o                                                                      
           |                                                                       
           |                                                                       
           |                                                                       
    57.3333+                                                                       
           |                                                                       
           |                                                                       
           |                                                                      o
           |                                                                       
    30.6667+                       o                                               
           |                                                                       
           |                                               o                       
         0 +---------+---------+---------+---------+---------+---------+---------+
           1.0       1.428571  1.857143  2.285714  2.714286  3.142857  3.571429  4.0       
                                         Iteration                               




Manage Results
^^^^^^^^^^^^^^^^^^^^^

You can also add results associated with an experiment.
You supply the experiment name, the metric and the value.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    project.add_result("Initial Exp", "rmse", 10.4)

The same can be done from the command line with ``add-result``:

.. code-block:: bash

    >projit add-result "Initial Exp" rmse 10.4

Note that ``add_result`` requires the named experiment to already be
registered with ``add_experiment`` (or ``start_experiment``) -- and, if you
pass a dataset name as shown below, that dataset must already be registered
with ``add_dataset`` as well. Calling ``add_result`` with an experiment or
dataset name that hasn't been registered raises an exception rather than
silently recording an orphaned result.

You can add as many metric as you want in an ad-hoc fashion.
There is no requirement for every experiment to track the same metrics.

Once you have finished running multiple experiments you can retrieve
a table with all experimental results.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    results = project.get_results()


This can also be done at the command line with the command:

.. code-block:: bash

    >projit list results


Experimental results can also be added such that they are associated with specific
datasets. This is useful to track performance on validation, test or holdouts sets.
As well as separate out-of-time test sets.

To add the results to a specific dataset, the dataset must be registered first:

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    project.add_dataset("MyTestDataSet", "data/test.csv")
    project.add_result("Initial Exp", "rmse", 10.4, "MyTestDataSet")

Or from the command line, with the dataset name as the fourth argument to
``add-result``:

.. code-block:: bash

    >projit add dataset MyTestDataSet data/test.csv
    >projit add-result "Initial Exp" rmse 10.4 MyTestDataSet

You can then list the results just for that specific dataset:

.. code-block:: bash

    >projit list results MyTestDataSet

Note the difference in argument meaning between ``add-result``/``add_result``
and ``list results`` above: the (required) positional argument to
``add-result``/``add_result`` is always the **experiment** name, and its
optional trailing argument is a **dataset** name to associate the result
with. The optional positional argument to ``projit list results`` is instead
a **dataset** name used to *filter* the results shown -- don't confuse the
two.



Compare Results
^^^^^^^^^^^^^^^^^^^^^

You can compare results across dataset using a simple CLI option.
The syntax requires that you provide a comma separates list of datasets as well as the metric you want to 
use for the comparison. If you want to compare multiple metrics you will need to create multiple tables.

For example

.. code-block:: bash

    >projit compare dataset1,dataset2,dataset3 RMSE


Will produce a table where each row corresponds to a specific experiment, 
and each column will correspond to one of the three specfied datasets. 
Within the table each cell will contain the RMSE of the experiment
on that dataset.

Note that the `compare` functionality support comparisons of arbitrary
numbers of datasets, but only a single parameter at a time.




