End-to-End Tutorial (API)
===========================

This tutorial walks through the same project lifecycle as
:doc:`tutorial_cli` -- initialisation, datasets, experiments, results,
comparison and reporting -- but using **only** the ``projit`` Python
package. No shell commands other than running your own scripts are
required.

For a topic-by-topic reference covering both CLI and API, see
:doc:`usage`.

.. note::
    projit is a metadata/bookkeeping layer around your project. It never
    imports, executes, or introspects your experiment scripts -- functions
    like ``start_experiment``/``end_experiment`` only bracket a timer and a
    metadata record around code that *you* run. Keep this in mind throughout
    the tutorial: every "run the experiment" step below is your own code,
    not something projit does for you.


1. Initialise and load the project
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Project initialisation (creating the ``.projit`` folder and template
directories) is normally done once via the CLI:

.. code-block:: bash

    >projit init "House Prices" default

From that point on, any script in the project can load it:

.. code-block:: python

    import projit as pit
    project = pit.projit_load()

``projit_load()`` locates the ``.projit`` configuration folder by walking up
from the current working directory, so this works regardless of where in
the project tree the script is executed from.


2. Register datasets
^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    project.add_dataset("train", "data/train.csv")
    project.add_dataset("test", "data/test.csv")

List the registered datasets by reading the ``datasets`` attribute directly
-- there is no separate ``list_datasets()`` method, ``datasets`` is a plain
public dictionary of ``{name: path}``:

.. code-block:: python

    for name, path in project.datasets.items():
        print(name, path)

Retrieve the path for a single dataset with ``get_dataset``:

.. code-block:: python

    train_path = project.get_dataset("train")

The path returned is relative to the project root, so it resolves correctly
no matter where your script runs from.


3. Register and run an experiment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The idiomatic way to record an experiment run is to bracket your own
training code with ``start_experiment`` and ``end_experiment``:

.. code-block:: python

    exec_id = project.start_experiment(
        "Baseline", "experiments/baseline.py",
        params={"seed": 42, "target": "price"},
    )

    # --- your training code goes here ---
    # e.g. model = train_model(seed=42, target="price")

    project.end_experiment(
        "Baseline", exec_id,
        hyperparams={"alpha": 0.01},
    )

``start_experiment`` registers the experiment if it isn't already
registered, and returns an execution ID that must be passed to
``end_experiment`` to close out that specific run.

``params`` and ``hyperparams`` are both opaque dictionaries stored on the
execution record -- projit does not read them or pass them to your script.
By convention, ``params`` records configuration known *before* the run
(dataset split, seed, target column) and ``hyperparams`` records values
decided or finalised *during or after* the run, but this is only a
convention: nothing enforces the split, and you can use either dict for
whatever you find useful. If you want ``seed``/``target`` to actually
configure the run, your own code needs to read them out of the ``params``
dict you passed in -- projit is only recording them for later reference.

Registering an experiment without tracking individual runs is also
possible, if you don't need execution timing:

.. code-block:: python

    project.add_experiment("Baseline", "experiments/baseline.py")


4. Record results
^^^^^^^^^^^^^^^^^^

.. code-block:: python

    project.add_result("Baseline", "rmse", 12.4)

Results can be tied to a specific dataset to track performance on
validation, test or holdout sets separately. The dataset must already be
registered. To compare a metric across datasets later (step 7), add a
dataset-scoped result for each dataset you plan to compare:

.. code-block:: python

    project.add_result("Baseline", "rmse", 12.1, "train")
    project.add_result("Baseline", "rmse", 11.9, "test")

Both calls require ``"Baseline"`` to already be registered via
``add_experiment`` or ``start_experiment`` -- calling ``add_result`` with an
unregistered experiment or dataset name raises an exception rather than
silently recording an orphaned result.


5. Retrieve results
^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    all_results = project.get_results()
    test_results = project.get_results("test")

Both calls return a ``pandas.DataFrame`` with one row per experiment.


6. Tag assets
^^^^^^^^^^^^^

.. code-block:: python

    project.add_tags("experiment", "Baseline", {"model": "linear", "version": "1"})
    values = project.get_tags("experiment", "Baseline", ["model", "version"])


7. Add a second experiment and compare
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    exec_id = project.start_experiment("RandomForest", "experiments/random_forest.py")
    # --- your training code goes here ---
    project.end_experiment("RandomForest", exec_id)

    project.add_result("RandomForest", "rmse", 10.5, "train")
    project.add_result("RandomForest", "rmse", 9.8, "test")

There is no ``project.compare(...)`` API method -- ``projit compare`` (CLI)
is presentation logic built on top of ``get_results(dataset)`` for each
dataset. Note that ``get_results(dataset)`` raises if no result has *ever*
been recorded against that dataset name (as opposed to returning an empty
table), which is why each dataset being compared needs at least one
dataset-scoped result first, as added above. The equivalent in a few lines
of pandas:

.. code-block:: python

    import pandas as pd

    def compare(project, datasets, metric):
        merged = None
        for dataset in datasets:
            rez = project.get_results(dataset)[["experiment", metric]]
            rez = rez.rename(columns={metric: dataset})
            merged = rez if merged is None else pd.merge(merged, rez, on="experiment")
        return merged

    compare(project, ["train", "test"], "rmse")

Likewise, the Markdown/LaTeX table formatting and the ASCII execution-time
plot available via the CLI's ``-m``/``-l`` flags and ``projit plot`` command
have no direct API equivalent -- they are CLI-side presentation features
over the same underlying data (``get_results``, ``get_execution_times``).


8. Render a report
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

    project.render("documentation/report.pdf")


9. Clean up
^^^^^^^^^^^

.. code-block:: python

    project.rm_dataset("test")
    project.rm_experiment(".")  # '.' removes every registered experiment

Unlike the CLI's ``rm`` command, the API calls do not ask for confirmation.
