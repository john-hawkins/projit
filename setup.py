# -*- coding: utf-8 -*-
 
"""setup.py: setuptools control."""

import re
from setuptools import setup

version = re.search(
        '^__version__\s*=\s*"(.*)"',
        open('projit/__init__.py').read(),
        re.M
    ).group(1) 

with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

setup(
    name = "projit",
    packages = ["projit"],
    license = "MIT",
    install_requires = ['pyyaml'],
    entry_points = {
        "console_scripts": ['projit = projit.cli:main']
    },
    include_package_data=True,
    version = version,
    description = "Python library and ccommand line application for data science project workflow management.",
    long_description = long_descr,
    long_description_content_type='text/markdown',
    author = "John Hawkins",
    author_email = "john@getting-data-science-done.com",
    url = "http://john-hawkins.github.io",
    project_urls = {
        'Documentation': "http://john-hawkins.github.io",
        'Source': "https://github.com/john-hawkins/projit",
        'Tracker': "https://github.com/john-hawkins/projit/issues" 
      }
    )

