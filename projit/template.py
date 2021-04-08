# -*- coding: utf-8 -*-
from __future__ import print_function
from io import StringIO
import datetime as dt
import pkg_resources
import codecs
import json
import sys
import os

########################################################################################
resource_package = __name__

def load_template(filename):
    """
    Utility function to load a project template
    """
    _path = '/'.join(('templates', filename))
    rawd = pkg_resources.resource_string(resource_package, _path).decode("utf-8")
    temp = json.loads(rawd)
    return temp

########################################################################################

"""
   This is a set of functions to allow the application to print time
   profiles of the various steps in a pipeline they are experimenting with
"""

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

profiles = {}

def initialise_profile():
    profiles = {}

def start_profile(proc_name):
    n1=dt.datetime.now()
    if proc_name in profiles:
        profiles[proc_name]["start"] = n1
    else:
        profiles[proc_name] = {"start":n1}

def end_profile(proc_name):
    n2 = dt.datetime.now()
    n1 = profiles[proc_name]["start"]
    total = n2-n1
    profiles[proc_name]["end"] = n2
    if "total" in profiles[proc_name]:
        curr_total = profiles[proc_name]["total"]
        profiles[proc_name]["total"] = curr_total + total
    else:
        profiles[proc_name]["total"] = total

def print_profiles():
    eprint("Computation Time Profile for each Pipeline Step")
    eprint("-----------------------------------------------")
    for k in profiles.keys():
        eprint(padded(k), str(profiles[k]["total"]) ) 

def padded(k, padto=20):
    spacer_len = padto - len(k)
    return k + (" "*spacer_len)

