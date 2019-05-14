#!/usr/bin/env python3
import os
import sys
import tempfile
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path

from __init__ import *
from dbquery import *

meownotes = create_app()

# test user credentials
TEST_USER = "kroshka"
TEST_PASSWORD = "test"

# fixture is called by the tests
@pytest.fixture
def client():
    db_fd, meownotes.config["DATABASE"] = tempfile.mkstemp()
    meownotes.config["TESTING"] = True
    client = meownotes.test_client()
    with meownotes.app_context():
        init_db()
    yield client
    os.close(db_fd)
    os.unlink(meownotes.config["DATABASE"])

def login(client, username, password):
    return client.post("/login", data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    return client.get("/logout", follow_redirects=True)

def cat(client):
    return client.get("/cat", follow_redirects=True)

def search(client, search_term):
    return client.post("/search", data=dict(
        search=search_term
    ), follow_redirects=True)

def dashboard(client):
    return client.get("/dashboard", follow_redirects=True)

def test_login_logout(client):
    """
    Check login and logout renders the right pages given the test user
    and test password of the user
    """
    rv = login(client, TEST_USER, TEST_PASSWORD)
    # dashboard page should be shown
    assert b"dashboard" in rv.data
    rv = logout(client)
    # landing page should be shown
    assert b"create a user or login with an existing one" in rv.data

def test_login_wrong_password(client):
    """
    Check that login fails when a wrong password is given
    """
    # first need to sign in 1x to create the user
    login(client, TEST_USER, TEST_PASSWORD)
    logout(client)
    # now try to sign in with the wrong password
    rv = login(client, TEST_USER, "wrongpwd")
    # landing page should be shown with the message
    assert b"The password was wrong" in rv.data

def test_random_cat(client):
    """
    Check that random cat
    """
    rv = cat(client)
    assert b"<img src" in rv.data

def test_dashboard(client):
    """
    Dashboard should show only to logged in user
    """
    login(client, TEST_USER, TEST_PASSWORD)
    rv = dashboard(client)
    # dashboard page should be shown
    assert b"dashboard" in rv.data


def test_search_page(client):
    """
    Check that the search page is shown when given a search
    """
    # check that search only available to logged in users
    rv = search(client, "Note")
    # landing page should be shown
    assert b"create a user or login with an existing one" in rv.data
    # with the user the search results page should be shown
    rv = login(client, TEST_USER, TEST_PASSWORD)
    rv = search(client, "Note")
    assert b"results" in rv.data