API
=====

To use projit within your Python scripts and applications include the package
and make use of the core API functions. In the following example we 
retrieve the project properties from an existing projit project.

.. code-block:: python

    import projit as pit
    project = pit.projit_load()

You can then use the project object to add or modify the datasets, experiments and results.

