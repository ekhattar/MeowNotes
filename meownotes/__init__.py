#!/usr/bin/env python3
"""
MeowNotes: the note-taking app for cat lovers
By Elias Khattar
2019
"""
import os
import sys
from flask import Flask, g, Blueprint
ROOT = os.path.dirname(os.path.realpath(__file__))
# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path
from config import Config
from dbquery import init_app

# Load if port is set in the environment
PORT = os.getenv("MEOWNOTES_PORT", None)
HOST = os.getenv("MEOWNOTES_HOST", "localhost")

def create_app():
    """
    Create MeowNotes from the blueprint
    """
    app = Flask(__name__)
    # Load the config
    app.config.from_object("config.Config")
    from pawprint import MEOW_BP
    # Register the main meownotes blueprint
    app.register_blueprint(MEOW_BP)
    init_app(app)
    return app

if __name__ == "__main__":
    """
    Used for local development
    to run this file directly with python
    """
    LOCAL_APP = create_app()
    if PORT is not None:
        LOCAL_APP.run(debug=True, host=HOST, port=PORT)
    else:
        LOCAL_APP.run(debug=True)
