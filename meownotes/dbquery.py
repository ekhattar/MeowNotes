#!/usr/bin/env python3
import sqlite3
import datetime
import operator
import os
import dateutil.parser
from utils import *

DEBUG = True

###### DB config

ROOT = os.path.dirname(os.path.realpath(__file__))
MEOWNOTES_DB = os.path.join(ROOT, "meownotes.db")

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
Expected form of parameters is:
[{"val": "", "cols": [], "type": None, "condition": False}]
"""
def prepare_query(template, table, parameters = [], search = False):
    # get the desired SQl string template
    query = eval(template)
    # replace with the desired table
    query = query.replace("TABLE", table)
    # parse the list of parameters to extract columns and values
    columns = []
    values = []
    conditions = []
    for parameter in parameters:
        # reformat the value if needed
        value = format_value_for_db(parameter["val"], parameter["cols"], parameter["type"])
        # add to the list of columns and values
        # if the cols and values are not conditions but data
        if not parameter["condition"]:
            values.append(value)
            columns.append(parameter["cols"][0])
        # handle conditions - possible types: exact, multi, contains
        elif "CONDITIONS" in query and parameter["condition"]:
            if parameter["type"] is "multi":
                conditions.append(value + " in " + "(" + ",".join(parameter["cols"]) + ")")
            elif parameter["type"] is "contains":
                conditions.append("(" + ",".join(parameter["cols"]) + ") LIKE " + value)
            else:
                conditions.append(parameter["cols"][0] + "=" + value)
    if "CONDITIONS" in query:
        query = query.replace("CONDITIONS", " AND ".join(conditions))
    if "COLS" in query and "VALS" in query:
        query = query.replace("COLS", ", ".join(columns))
        query = query.replace("VALS", ", ".join(values))
    if DEBUG:
        print(query)
    return query

###### Functions to interact with the MeowNotes SQLite database ######
prepare_query("GET_ALL", "users")
prepare_query("GET_CONDITIONAL", "users", [{"val": "kroshka", "cols": ["username"], "type": "exact", "condition": True}, {"val": 1, "cols": ["uid"], "type": "exact", "condition": True}])
prepare_query("INSERT", "users", [{"val": "kroshka", "cols": ["username"], "type": "exact", "condition": False}, {"val": 1, "cols": ["uid"], "type": "exact", "condition": False}])
prepare_query("UPDATE_CONDITIONAL", "users", [{"val": "kroshka", "cols": ["username"], "type": "exact", "condition": False}, {"val": 1, "cols": ["uid"], "type": "exact", "condition": True}])