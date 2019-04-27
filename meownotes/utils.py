#!/usr/bin/env python3

###### Generic utilities

"""
Format integers for inserting/searching in the DB
"""
def format_value_for_db(value, cols, paramtype):
    if type(value) == int or "id" in cols:
        result = str(value)
    elif paramtype == "contains":
        result = "'%" + value + "%'"
    else:
        result = "'" + value + "'"
    return result