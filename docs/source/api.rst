API
=====

To use projit within your Python scripts and applications include the package
and make use of the core API functions. In the following example we
retrieve the project properties from an existing projit project.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()

You can then use the project object to add or modify the datasets, experiments and results.

For a full worked example that uses only the Python API to take a project
through its entire lifecycle -- init, datasets, experiments, results,
comparison, reporting -- see :doc:`tutorial_api`.

.. important::
    projit is a metadata/bookkeeping layer around your project. It never
    imports, executes, or introspects your experiment scripts.
    ``start_experiment``/``end_experiment`` only bracket a timer and a
    metadata record around code that *you* run yourself; ``params`` and
    ``hyperparams`` are stored as-is and are never read by projit or passed
    into your script.

## API Functions 

.. autosummary::
   :toctree: generated

   projit



