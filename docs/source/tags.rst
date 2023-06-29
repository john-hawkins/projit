Asset Tags
===========

Projit allows you to tag your various assets and then use them when querying
and displaying summaries of a project


Command Line Tagging
^^^^^^^^^^^^^^^^^^^^

Add tags to any project asset with a simple commnand line option

.. code-block:: bash

    >projit tag dataset train type=tabular,source=Kaggle

This command will create two tags for for the dataset `train` one for `type` with the value
`tabular` and another for source with the value `Kaggle`

These tags will not be included by default when you list the datasets, but can be included
by using an optional CLI switch, as follows:


.. code-block:: bash

    >projit list datasets --tags source type
 
    __Datasets________________________________________________________________________________
    __Name____source___type______Path_________________________________________________________
      train   Kaggle   tabular   data/processed.csv


The command will now include the tags in the listing as is shown above.


Tagging Experiments
^^^^^^^^^^^^^^^^^^^^^

You can add tags to experiments using the CLI

.. code-block:: bash

    >projit tag experiment "Initial Exp" algo=NaiveBayes

This command is adding an indication of the algorithm used in the named experiment.
These tags could be for feature engineering, sampling or any ad hoc element of your data science
methodology. The best practice is to determine a naming convention and Ontology for tagging your
experiments so that you can make meaningful comaprisons across projects.

This tagging can also be done programmatically using the python API.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    tags = {"algo":"NaiveBayes"}
    project.add_experiment("Initial Exp", "experiments/exp_one.py", tags=tags)

Tagging can also be applied when starting the experiment.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()
    tags = {"algo":"NaiveBayes"}
    exec_id = project.start_experiment("Initial Exp", "experiments/exp_one.py", params={}, tags=tags)
    #
    # INSERT ALL EXPERIMENT CODE HERE
    #
    project.end_experiment("Initial Exp", exec_id, hyperparams={})


Tags can also be include when you list the experiments using the CLI:

.. code-block:: bash

    >projit list experiments --tags algo

    __Experiments_______________________________________________________________________________
    __Name_____________algo________Runs__MeanTime____Path_______________________________________
      Initial Exp      NaiveBayes  4     42s         experiments/exp_one.py
      Second Exp       ExtraTrees  2     19s         experiments/exp_two.py


This will produce a table that includes the specified tags along with the default information
about your experiments.

