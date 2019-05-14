#!/usr/bin/env python3
import sqlite3
import datetime
import operator
import os
import sys
import dateutil.parser
import click
from flask import current_app, g
from flask.cli import with_appcontext

ROOT = os.path.dirname(os.path.realpath(__file__))

# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path

from utils import *

# App config - determines if debug output is shown in the console
DEBUG = os.getenv("MEOWNOTES_DEBUG", False)

if DEBUG:
    print(">>> INFO: MeowNotes DEBUG is set to true!")

############ DB config ############

# DB connection created using help of tutorial from flask
# http://flask.pocoo.org/docs/1.0/tutorial/database/

def get_db():
    print(current_app.config["DATABASE"])
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource("meownotes-schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

# can now create a fresh db using the command line
# flask initdb
@click.command("initdb")
@with_appcontext
def init_db_command():
    # clear existing data
    # create new tables according to the schema
    init_db()
    click.echo("Initialized the MeowNotes database.")

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

############ Functions to interact with the MeowNotes SQLite database ############

def execute_select(query):
    db = get_db()
    result = db.execute(query).fetchall()
    if DEBUG:
        print(result)
    return result

def execute_and_commit(query):
    db = get_db()
    db.execute(query)
    db.commit()

############ SQL query templates where "PARAMETERS" will be replaced ############

# basic queries structure
GET_ALL = "SELECT * from TABLE"
GET_CONDITIONAL = "SELECT * from TABLE WHERE CONDITIONS" # e.g., SELECT * from users WHERE username='kroshka' AND uid=1
INSERT = "INSERT INTO TABLE (COLS) VALUES (VALS)" # e.g., INSERT INTO users (username, uid) VALUES ('kroshka', 1)
DELETE_ALL = "DELETE FROM TABLE"
DELETE_CONDITIONAL = "DELETE from TABLE WHERE CONDITIONS" # e.g., DELETE from users WHERE username='kroshka' AND uid=1
UPDATE_CONDITIONAL = "UPDATE TABLE SET PARAMETERS WHERE CONDITIONS" # e.g., UPDATE table SET column1 = value1, column2 = value2, ... WHERE condition;

"""
Forms the proper query using the given template and replacement values
Expected form of query_input_items is:
[{"val": "", "cols": [], "type": None, "condition": False}]
Example use:
prepare_query("GET_CONDITIONAL", "users", [{"val": "kroshka", "cols": ["username"], "type": "exact", "condition": True}, 
                                           {"val": 1, "cols": ["uid"], "type": "exact", "condition": True}])
"""
def prepare_query(template, table, query_input_items = []):
    # get the desired SQl string template
    query = eval(template)
    # replace with the desired table
    query = query.replace("TABLE", table)
    # parse the inputs to extract columns and values
    columns = []
    values = []
    # parameters are combos of columns and values that are not conditions
    parameters = []
    # conditions are conditions that must be fulfilled, possible types (affect string form): exact, multi, contains
    conditions = []
    for item in query_input_items:
        # reformat the value if needed
        value = format_value_for_db(item["val"], item["cols"], item["type"])
        # add to the list of columns and values
        # if the cols and values are not conditions but data
        if item["condition"] is False:
            values.append(value)
            columns.append(item["cols"][0])
            parameters.append(item["cols"][0] + "=" + value)
        # handle conditions
        elif "CONDITIONS" in query and item["condition"] is True:
            if item["type"] is "multi":
                conditions.append(value + " in " + "(" + ",".join(item["cols"]) + ")")
            elif item["type"] is "contains":
                conditions.append("(" + ",".join(item["cols"]) + ") LIKE " + value)
            else:
                conditions.append(item["cols"][0] + "=" + value)
    if "CONDITIONS" in query:
        query = query.replace("CONDITIONS", " AND ".join(conditions))
    if "COLS" in query and "VALS" in query:
        query = query.replace("COLS", ", ".join(columns))
        query = query.replace("VALS", ", ".join(values))
    if "PARAMETERS" in query:
        query = query.replace("PARAMETERS", ", ".join(parameters))
    if DEBUG:
        print(query)
    return query

############ MeowNotes-specific functions for DB interaction ############

"""
Retrieve all entries from a given table
if UID is given, will limit to that user
"""
def get_all(table, uid = None):
    if uid is None:
        query = prepare_query("GET_ALL", table)
        results = execute_select(query)
    else:
        query_input_items = [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True}]
        query = prepare_query("GET_CONDITIONAL", table, query_input_items)
        results = execute_select(query)
    return results

"""
Deletes all entries from a given table
if UID is given, will limit to that user
"""
def delete_all(table, uid = None):
    if uid is None:
        query = prepare_query("DELETE_ALL", table)
    else:
        query_input_items = [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True}]
        query = prepare_query("DELETE_CONDITIONAL", table, query_input_items)
    try:
        execute_and_commit(query)
    except Exception as e:
        msg = "Notes were unable to be deleted! Error: %s" + str(e)
    if DEBUG:
        print(msg)
    return msg

# USER-specific functions

def get_user_by_name(username):
    query_input_items = [{"val": username, "cols": ["username"], "type": "exact", "condition": True}]
    query = prepare_query("GET_CONDITIONAL", "users", query_input_items)
    results = execute_select(query)
    return results

def get_user_by_id(uid):
    query_input_items = [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True}]
    query = prepare_query("GET_CONDITIONAL", "users", query_input_items)
    results = execute_select(query)
    return results

def get_id_by_user(username):
    db_res = get_user_by_name(username)
    db_user = parse_user(db_res[0])
    uid = db_user["uid"]
    return uid

def delete_user_by_id(uid):
    query_input_items = [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True}]
    query = prepare_query("DELETE_CONDITIONAL", "users", query_input_items)
    try:
        execute_and_commit(query)
        msg = "User with id '%s' was deleted." % str(uid)
    except Exception as e:
        msg = "User was unable to be deleted! Error: %s" + str(e)
    if DEBUG:
        print(msg)
    return msg

"""
Create a new user if that username is not taken
Example use: create_user("kroshka", "love")
"""
def create_user(username, password):
    # make username lowercase
    username = username.lower()
    # prepare the query
    query_input_items = [{"val": username, "cols": ["username"], "type": "exact", "condition": False},
        {"val": password, "cols": ["password"], "type": "exact", "condition": False}]
    query = prepare_query("INSERT", "users", query_input_items)
    # if the user already exists, return a warning message
    try:
        execute_and_commit(query)
        msg = "Welcome! An account for %s was created!" % username
    except sqlite3.IntegrityError:
        msg = "Oh no! That username already exists! Please choose another one (or enter the correct password)."
    if DEBUG:
        print(msg)
    return msg

# NOTE-specific functions

def get_notes_by_user(uid):
    query_input_items = [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True}]
    query = prepare_query("GET_CONDITIONAL", "notes", query_input_items)
    results = execute_select(query)
    return results

def get_note_by_id(uid, note_id):
    query_input_items = [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True},
        {"val": note_id, "cols": ["id"], "type": "exact", "condition": True}]
    query = prepare_query("GET_CONDITIONAL", "notes", query_input_items)
    results = execute_select(query)
    return results

def delete_note_by_id(uid, note_id):
    query_input_items = [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True},
        {"val": note_id, "cols": ["id"], "type": "exact", "condition": True}]
    query = prepare_query("DELETE_CONDITIONAL", "notes", query_input_items)
    try:
        execute_and_commit(query)
        msg = "Note with id '%s' was deleted." % str(note_id)
    except Exception as e:
        msg = "Note was unable to be deleted! Error: %s" + str(e)
    if DEBUG:
        print(msg)
    return msg

"""
Create a new note given a title, tags, and content
Example use: create_note(1, "Test Title", "uni,se", "Content of the note about uni")
"""
def create_note(uid, title, tags, content):
    timestamp = datetime.datetime.now().isoformat()
    # check if the tags are an array, if yes make them a comma-separated string
    tags = fix_tags(tags)
    query_input_items = []
    inputs = [(uid, ["uid"]), (timestamp, ["date_created"]), (title, ["title"]), (tags, ["tags"]), (content, ["content"])]
    for input in inputs:
        query_input_items.append(create_input_obj(input[0], input[1]))
    query = prepare_query("INSERT", "notes", query_input_items)
    # try to insert
    try:
        execute_and_commit(query)
        msg = "Note with title '%s' was created." % title
    except Exception as e:
        msg = "Note was unable to be created! Error: %s" + str(e)
    if DEBUG:
        print(msg)
    return msg

"""
Update an existing note by the uid and note id
Example use: update_note(1,1, "New note title", "", "This is a note with content")
"""
def update_note(uid, note_id, title, tags, content):
    # check if the tags are an array, if yes make them a comma-separated string
    tags = fix_tags(tags)
    query_input_items = []
    inputs = [(uid, ["uid"], "exact", True), (note_id, ["id"], "exact", True), (title, ["title"], None, False), (tags, ["tags"], None, False), (content, ["content"], None, False)]
    for input in inputs:
        query_input_items.append(create_input_obj(input[0], input[1], input[2], input[3]))
    query = prepare_query("UPDATE_CONDITIONAL", "notes", query_input_items)
    # try to modify
    try:
        execute_and_commit(query)
        msg = "Note with title '%s' was modified." % title
    except Exception as e:
        msg = "Note was unable to be modified! Error: %s" + str(e)
    if DEBUG:
        print(msg)
    return msg

"""
Retrieve all notes for the current user that match the search
searches the "title", "tags", and "content" columns
returns a list of notes
Example output: [(1, 1, '2019-05-05T16:15:14.429235', 'My First Note', 'uni', 'This is the text of the note.')]
"""
def get_search_notes(uid, search_string, search_fields = None):
    # search for matches in the TITLE for this user
    title_query = prepare_query("GET_CONDITIONAL", "notes", [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True},
        {"val": search_string, "cols": ["title"], "type": "contains", "condition": True}])
    title_results = execute_select(title_query)
    # search for matches in the TAGS for this user
    tags_query = prepare_query("GET_CONDITIONAL", "notes", [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True},
        {"val": search_string, "cols": ["tags"], "type": "contains", "condition": True}])
    tags_results = execute_select(tags_query)
    # search for matches in the CONTENT for this user
    contents_query = prepare_query("GET_CONDITIONAL", "notes", [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True},
        {"val": search_string, "cols": ["content"], "type": "contains", "condition": True}])
    contents_results = execute_select(contents_query)
    # combine the three result lists
    results = []
    if search_fields is not None:
        if "title" in search_fields:
            results += title_results
        if "tags" in search_fields:
            results += tags_results
        if "content" in search_fields:
            results += contents_results
    else:
        results = title_results + tags_results + contents_results
    # convert into a set in order to remove duplicate results
    # then convert back into a list
    results = list(set(results))
    return results

############ Functions to parse db results and return as objects ############

# Takes a single user row DB result and puts it into a parsable form
def parse_user(db_result):
    result = {
        "uid": db_result[0],
        "username": db_result[1],
        "password": db_result[2]
    }
    return result

def parse_note(db_note):
    # include a datetime that can be output directly in the ui
    real_date = dateutil.parser.parse(db_note[2])
    result = {
        "note_id": db_note[0],
        "uid": db_note[1],
        "date_created": db_note[2],
        "ui_date": real_date.strftime('%b %d, %H:%m'),
        "title": db_note[3],
        "tags": db_note[4].split(","),
        "content": db_note[5],
    }
    return result

# Takes a list of DB note results and puts them into a parsable list of objects
def process_note_results(db_notes):
    parsed_notes = []
    # Make a list of note objects
    for db_note in db_notes:
        parsed_notes.append(parse_note(db_note))
    # Sort the list by date
    parsed_notes.sort(key=operator.itemgetter('date_created'))
    return parsed_notes

