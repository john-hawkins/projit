#!/bin/bash

rm ./source/projit.rst
rm ./source/modules.rst

make clean
sphinx-apidoc -o ./source ../projit
make html


