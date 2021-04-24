Usage Guide
===========

Usage of projit happens at multiple points in a project development

Initialise a project as follows

.. code-block:: bash

    >projit init "Project Name"

This command will prompt you to provide a project deascription and then
create the projit configuration folder then write the project properties file.

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

Note that the following syntax will work regardless of where in the directory structure the
script is extected. The projit Project determines the path to the data with the condition that
when you record the data it must be given a path relative to the root directory of the project.


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

You can also add results associated with an experiment. 
You just supply the experiment name, the metric and the value.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    project.add_result("Initial Exp", "rmse", 10.4)

You can add as many metric as you want in an ad-hoc fashion.

Once you have finished running multiple experiments you can retrieve
a table with all experimental results.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    results = project.get_results()




