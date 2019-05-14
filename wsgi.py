#!/usr/bin/env python3
import sys
import os

# check if running the server locally
LOCALDEV = os.getenv("MEOWNOTES_LOCALDEV", False)

if LOCALDEV:
    # take the path of the current file
    project_home = os.path.join(os.path.dirname(os.path.realpath(__file__)), "meownotes")
else:
    # use the pythonanywhere path
    project_home = "/home/ekhattar/MeowNotes/meownotes"

# add the project directory to the sys.path
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# needs to be called "application" for pythonanywhere WSGI to work
from __init__ import app as application 
