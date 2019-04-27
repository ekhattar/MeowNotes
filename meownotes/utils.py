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

"""
Used to generate larger input objects for the query creation e.g., by iterating in a list
Example use: create_input_obj(1, "uid")
Output form: [{"val": uid, "cols": ["uid"], "type": "exact", "condition": True}]
"""
def create_input_obj(val, cols_list, input_type = None, condition = False):
    input_obj = {"val": val, "cols": cols_list, "type": input_type, "condition": condition}
    return input_obj

"""
Handles the tags
Checks if the tags are an array, if yes make them a comma-separated string
"""
def fix_tags(tags):
    if isinstance(tags, list):
        tags = ",".join(tags)
    return tags