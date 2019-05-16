#!/usr/bin/env python3
"""
MeowNotes Flask app config file
"""
from datetime import timedelta
import os

ROOT = os.path.dirname(os.path.realpath(__file__))
MEOWNOTES_DB = os.path.join(ROOT, "meownotes.db")

class Config():
    """
    Main config for MeowNotes
    """
    DATABASE = MEOWNOTES_DB
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = "null"
    SESSION_COOKIE_NAME = "MeowNotes"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
