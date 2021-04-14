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

TODO

