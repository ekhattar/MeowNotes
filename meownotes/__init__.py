#!/usr/bin/env python3
from flask import Flask, g, Blueprint
import os
import sys

ROOT = os.path.dirname(os.path.realpath(__file__))

# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path

from dbquery import *
from utils import *
from config import Config

# Load if port is set in the environment
PORT = os.getenv("MEOWNOTES_PORT", None)
HOST = os.getenv("MEOWNOTES_HOST", "localhost")

def create_app():

    app = Flask(__name__)

    # Load the config
    app.config.from_object("config.Config")
    from pawprint import bp
    # Register the main meownotes blueprint
    app.register_blueprint(bp)

    init_app(app)
    return app

if __name__ == "__main__":
    app = create_app()
    if PORT is not None:
        app.run(debug=True, host=HOST, port=PORT)
    else:
        app.run(debug=True)
