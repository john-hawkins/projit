End-to-End Tutorial (CLI)
==========================

This tutorial walks through the entire lifecycle of a small data science
project -- initialisation, datasets, experiments, results, comparison,
plotting and reporting -- using **only** ``projit`` shell commands. No
Python code is required for any of these steps.

If you want the equivalent walkthrough using the Python API instead, see
:doc:`tutorial_api`. For a topic-by-topic reference covering both CLI and
API, see :doc:`usage`.

The example project below predicts house prices from two datasets
(``train`` and ``test``) using two candidate models.


1. Initialise the project
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    >projit init "House Prices" default

The ``default`` template creates ``data/``, ``experiments/`` and
``documentation/`` directories alongside the ``.projit`` configuration
folder.

.. code-block:: bash

    >projit status

    Project: House Prices
    Description:
    Datasets: 0
    Experiments: 0
    Executions: 0


2. Register datasets
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    >projit add dataset train data/train.csv
    >projit add dataset test data/test.csv

.. code-block:: bash

    >projit list datasets

    __Datasets________________________________________________________
    __Name______Path_________
      train      data/train.csv
      test       data/test.csv

Datasets can be re-registered at any time to update their path -- adding a
dataset with a name that already exists overwrites the old path.


3. Register and run an experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An experiment can be registered on its own with ``add``:

.. code-block:: bash

    >projit add experiment "Baseline" experiments/baseline.py

To also record *when* the experiment was run and how long it took, use
``start`` and ``stop`` instead. ``projit start`` does not execute your
script for you -- it only registers a timestamped execution record and
prints an execution ID, which you pass to ``projit stop`` once your script
finishes:

.. code-block:: bash

    EXEC_ID=$(projit start "Baseline" experiments/baseline.py)
    python experiments/baseline.py
    projit stop "Baseline" "$EXEC_ID"

``projit start`` registers the experiment automatically if it isn't already
registered, so the earlier ``projit add experiment`` step is optional if
you're always going to run the experiment through ``start``/``stop``.

Repeat the ``start`` / run / ``stop`` sequence each time you re-run the
experiment (e.g. after changing hyperparameters). Each run adds a new
execution record.


4. Record results
^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    >projit add-result "Baseline" rmse 12.4

Results can also be tied to a specific dataset, which is useful for
tracking performance on validation, test or holdout sets separately. To
compare a metric across datasets later (step 7), add a dataset-scoped result
for each dataset you plan to compare:

.. code-block:: bash

    >projit add-result "Baseline" rmse 12.1 train
    >projit add-result "Baseline" rmse 11.9 test

Both the experiment and (if given) the dataset must already be registered,
otherwise the command fails with an error rather than silently recording an
orphaned result.


5. List experiments and results
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    >projit list experiments

    __Experiments___________________________________________________________________
    __Name_____________Runs__MeanTime____Path_______________________________________
      Baseline          1        3s      experiments/baseline.py

.. code-block:: bash

    >projit list results

.. code-block:: bash

    >projit list results test

Note the difference in argument meaning between ``add-result`` and
``list results``: the (required) positional argument to ``add-result`` is
always the **experiment** name, while the optional positional argument to
``list results`` is a **dataset** name used to filter the output.


6. Tag assets
^^^^^^^^^^^^^

.. code-block:: bash

    >projit tag experiment "Baseline" model=linear,version=1
    >projit list experiments --tags model --tags version


7. Add a second experiment and compare
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    EXEC_ID=$(projit start "RandomForest" experiments/random_forest.py)
    python experiments/random_forest.py
    projit stop "RandomForest" "$EXEC_ID"
    projit add-result "RandomForest" rmse 10.5 train
    projit add-result "RandomForest" rmse 9.8 test

Compare a metric for both experiments, across both datasets, in one table.
``compare`` reads dataset-scoped results, so each dataset being compared
needs at least one result recorded against it first (as above) -- comparing
a dataset with no dataset-scoped results raises an error:

.. code-block:: bash

    >projit compare train,test rmse

``compare`` supports comparisons across any number of datasets, but only
one metric at a time -- to compare a second metric, run it again.

Use ``-m`` or ``-l`` before any subcommand to switch the output of
``list results`` and ``compare`` to Markdown or LaTeX:

.. code-block:: bash

    >projit -m compare train,test rmse


8. Plot execution times
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    >projit plot "Baseline" execution

    __Experiment_[Baseline]_execution_time_______________________________________
    Seconds
    ...

.. note::
    ``projit plot`` also accepts ``hyperparam`` and ``result`` as the
    property to plot, but these are not yet implemented (they print
    ``TODO``). Only ``execution`` produces a plot today.


9. Render a report
^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

    >projit render documentation/report.pdf


10. Clean up
^^^^^^^^^^^^

.. code-block:: bash

    >projit rm dataset test
    Remove dataset named test. Please confirm (y/n)
    >y

    >projit rm experiment .
    Remove all experiments. Please confirm (y/n)
    >y

``rm`` always asks for confirmation. Use the ``.`` wildcard in place of a
name to remove every dataset or experiment of that type in one go.
