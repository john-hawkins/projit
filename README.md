# ProjIt
### Project Integration for Data Science Work 

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/john-hawkins/projit/actions/workflows/python-package.yml/badge.svg)](https://github.com/john-hawkins/projit/actions/workflows/python-package.yml)
<!--
[![PyPI](https://img.shields.io/pypi/v/projit.svg)](https://pypi.org/project/projit)
-->

Projit is a tool for managing Data Science Project structure, properties, data, experiments & collaboration.

The goal of this project is to allow data science teams to work on
projects in a structured and standardized way. The projit utility
allows you to establish a project according to a configurable template.
It then provides a python library that can be used inside experiments and
scripts so that references to training, evaluations and test data sets
is standardized.

This project was inspired by a combination of the CookieCutter template
and the Git utility.



Released and distributed via setuptools/PyPI/pip for Python 3.
 
Additional detail available in the [documentation](https://john-hawkins.github.io)

Built using the 
[bootstrap cmdline template](https://github.com/jgehrcke/python-cmdline-bootstrap)
 by [jgehrcke](https://github.com/jgehrcke)


## Notes

Initial implementation is focused allowing the user to initialise a project, and then
modify it using a python package that can be called independently in scripts across 
the project structure. This creates a central authority for updating and retrieving
info about data sets and experimental results.

## Usage

You can use this application multiple ways

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
python setup.py install
```

(or via pip from PyPI):

```
pip install projit
```

Now, the ``projit`` command is available::

```
projit init "Test Project"
```

This will initialise the current directory as a Data Science Project using
the default template. Please refer to the [docs for more detail]().

