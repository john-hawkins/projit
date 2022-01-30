TODO LIST
=========

* Extend work on Experiment Executions
  * Modify results recording so that is associated with executions
  * Include executions info in experiment listing
  * Add functionality to visualise execution time / params / hyperparams
    * Potenitally plotting results against the above

* Improve documentation rendering
  * Existing prototype renders basic info into a simple PDF
  * Consider designing a template system for documentation rendering 

* Consider adding a default Makefile that can execute data prep and experiments
  * Add data prep registration
  * Change experiment registration to make paths executable.
  * Consider adding parameterisation
  * Determine failure conditions

* Add R package to emulate core package functions
  * Retrieve paths to data
  * Start and end experiments
  * Register Results

* Allow user to register a canonical way to read data
  * e.g. if the default `read_csv` in Python or R makes encoding mistakes
  * e.g. if there are specific variable typings or date conversions to enforce
  * Tis method could then be transparently reused in every experiment.

