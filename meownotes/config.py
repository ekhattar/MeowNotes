#!/usr/bin/env python3
from datetime import timedelta
import os

class Config():
    SECRET_KEY = os.urandom(24)
    SESSION_TYPE = "null"
    SESSION_COOKIE_NAME = "MeowNotes"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=10)
