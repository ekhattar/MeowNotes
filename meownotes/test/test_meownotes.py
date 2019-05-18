#!/usr/bin/env python3
import os
import sys
import tempfile
import pytest
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path
from __init__ import create_app
from dbquery import init_db

meownotes = create_app()

# test user credentials
TEST_USER = "kroshka"
TEST_PASSWORD = "test"

# a fixture is called by the tests when running
# created using the flask documentation http://flask.pocoo.org/docs/1.0/testing/

# START section based on documentation
@pytest.fixture
def client():
    """
    Used for all tests; sets up test db
    """
    db_fd, meownotes.config["DATABASE"] = tempfile.mkstemp()
    meownotes.config["TESTING"] = True
    client = meownotes.test_client()
    with meownotes.app_context():
        init_db()
    yield client
    os.close(db_fd)
    os.unlink(meownotes.config["DATABASE"])

# END section based on documentation

############ Helper section ############

def login(client, username, password):
    """Login"""
    return client.post("/login", data=dict(
        username=username,
        password=password
    ), follow_redirects=True)

def logout(client):
    """Logout"""
    return client.get("/logout", follow_redirects=True)

def cat(client):
    """See a cat"""
    return client.get("/cat", follow_redirects=True)

def search(client, search_term):
    """Search"""
    return client.post("/search", data=dict(
        search=search_term
    ), follow_redirects=True)

def dashboard(client):
    """Go to the dashboard"""
    return client.get("/dashboard", follow_redirects=True)

def create_note(client, title, tags, content):
    """Create a note"""
    return client.post("/create", data=dict(
        title=title,
        tags=tags,
        content=content
    ), follow_redirects=True)

def view_note(client, note_id):
    """View a note"""
    url_path = "/view?id=" + note_id
    return client.get(url_path, follow_redirects=True)

def update_note(client, note_id, title, tags, content):
    """Update an existing note"""
    return client.post("/update", data=dict(
        note_id=note_id,
        title=title,
        tags=tags,
        content=content
    ), follow_redirects=True)

def delete_note(client, note_id):
    """Delete a note"""
    return client.post("/delete", data=dict(
        note_id=note_id
    ), follow_redirects=True)

############ Tests section ############

def test_login_logout(client):
    """
    Check login and logout renders the right pages given the test user
    and test password of the user
    """
    result = login(client, TEST_USER, TEST_PASSWORD)
    # dashboard page should be shown
    # note that the b" is needed for asserts otherwise
    # TypeError: a bytes-like object is required, not 'str' 
    assert b"dashboard" in result.data
    result = logout(client)
    # landing page should be shown when the user is NOT logged in
    assert b"create a user or login with an existing one" in result.data

def test_login_wrong_password(client):
    """
    Check that login fails when a wrong password is given
    """
    # first need to sign in 1x to create the user
    login(client, TEST_USER, TEST_PASSWORD)
    logout(client)
    # now try to sign in with the wrong password
    result = login(client, TEST_USER, "wrongpwd")
    # landing page should be shown with the message
    assert b"wrong password" in result.data

def test_random_cat(client):
    """
    Check that random cat is shown
    (accessible logged in and out)
    """
    result = cat(client)
    assert b"<img src" in result.data

def test_dashboard(client):
    """
    Dashboard should show only to logged in user
    """
    login(client, TEST_USER, TEST_PASSWORD)
    result = dashboard(client)
    # dashboard page should be shown
    assert b"dashboard" in result.data

def test_search_page(client):
    """
    Check that the search page is shown when given a search
    """
    # check that search only available to logged in users
    result = search(client, "Note")
    # landing page should be shown
    assert b"create a user or login with an existing one" in result.data
    # with the user the search results page should be shown
    result = login(client, TEST_USER, TEST_PASSWORD)
    result = search(client, "Note")
    assert b"results" in result.data

def test_create_note(client):
    """
    User should create a note
    """
    login(client, TEST_USER, TEST_PASSWORD)
    result = create_note(client, "Note 1", "test", "The original note contents")
    # dashboard page should be shown
    assert b"dashboard" in result.data

def test_view_note(client):
    """
    User should view a note
    """
    login(client, TEST_USER, TEST_PASSWORD)
    create_note(client, "Note 1", "test", "The original note contents")
    result = view_note(client, "1")
    # view a note page should be shown
    assert b"The original note contents" in result.data
    # viewing a note given an id that doesn't exist
    result = view_note(client, "2")
    # the warning should be shown (flask flash)
    assert b"note not found" in result.data

def test_update_note(client):
    """
    Updating a note should redirect back to the note
    and show a notification the note was updated
    """
    login(client, TEST_USER, TEST_PASSWORD)
    create_note(client, "Note 1", "test", "The original note contents")
    result = view_note(client, "1")
    assert b"The original note contents" in result.data
    result = update_note(client, "1", "Note 1", "test", "The updated note contents")
    assert b"The updated note contents" in result.data

def test_delete_note(client):
    """
    Deleting a note should redirect to the dashboard
    and show a warning
    """
    login(client, TEST_USER, TEST_PASSWORD)
    create_note(client, "Note 1", "test", "The original note contents")
    result = delete_note(client, "1")
    assert b"note deleted" in result.data
