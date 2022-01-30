# Projit
### Project Integrator for Decoupled Data Science

> Status: **Beta** Functional.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/john-hawkins/projit/actions/workflows/python-package.yml/badge.svg)](https://github.com/john-hawkins/projit/actions/workflows/python-package.yml)
[![Documentation Status](https://readthedocs.org/projects/projit/badge/?version=latest)](https://projit.readthedocs.io/en/latest/?badge=latest)
[![PyPI](https://img.shields.io/pypi/v/projit.svg)](https://pypi.org/project/projit)

Projit is a utility to help data scientists manage projects that contain multiple experiments
and components that need to interact in a de-coupled manner. 
Use it to define and manage project structure, properties, data, experiments & collaboration.

The goal of this project is to allow data scientists and teams to work on projects in
a structured and standardized way. The projit utility allows you to establish a
project with a centralised meta-data repository. This meta-data is used by the
application and package to facilitate loosely coupled communication between
scripts for experiments, to track results and parameters.

For example, projit provides a python library that can be used inside
experiments and scripts so references to training, evaluation and test data
sets can accessed without passing around and maintaing paths.

In addition the project can be initialised according to a standardized layout
so that the diectory structure is familiar to all team members.

This project was inspired by a combination of other projects:
* [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
* [The Python CookieCutter Application](https://cookiecutter.readthedocs.io/)
* [The Git Source Control Utility]()

Released and distributed via setuptools/PyPI/pip for Python 3.

Additional details and usage instructions available in the [documentation](https://projit.readthedocs.io)


## Notes

Initial implementation is focused allowing the user to initialise a project,
and then modify it using a python package that can be called independently in
scripts across the project structure. This creates a central authority for
updating and retrieving info about data sets and experimental results.

## Usage

You can use this application in multiple ways

Use the runner:

```
./projit-runner.py init "Test Project"
```

Invoke the directory as a package:

```
python -m projit init "Test Project"
```

Or simply install the package and use the command line application directly
as shown in the process below:

# Installation

Installation from the source tree:

```
git clone https://github.com/john-hawkins/projit
cd projit
python setup.py install
```

(or via pip from PyPI):

```
pip install projit
```

Now, the ``projit`` command is available:

```
projit init "Test Project"
```

This will initialise the current directory as a Data Science Project using the
default template. Please refer to the
[documentation for more detail on projit commands](https://projit.readthedocs.io).

## Output

By adding experiments and results to a projit project you can examine them.
Example output in the table below:


Results on [test] 
-----------------
| experiment | MAE      | MAPE   |
| ----------:| --------:| ------:|
| mytest     | 11230.46 |  13.46 |
| mytest2    |      nan |  15.86 |


# Acknowledgements

Python package built using the
[bootstrap cmdline template](https://github.com/jgehrcke/python-cmdline-bootstrap)
 by [jgehrcke](https://github.com/jgehrcke)


