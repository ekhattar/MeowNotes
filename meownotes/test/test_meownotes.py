#!/usr/bin/env python3
import os
import sys
import tempfile
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path

from __init__ import app as meownotes

@pytest.fixture
def client():
    db_fd, meownotes.config['DATABASE'] = tempfile.mkstemp()
    meownotes.config['TESTING'] = True
    client = meownotes.test_client()

    with meownotes.app_context():
        meownotes.init_db()

    yield client

    os.close(db_fd)
    os.unlink(meownotes.config['DATABASE'])

def test_empty_db(client):
    """Start with a blank database."""

    rv = client.get('/')
    assert b'No entries here so far' in rv.data