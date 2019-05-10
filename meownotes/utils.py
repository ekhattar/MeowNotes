#!/usr/bin/env python3
import random

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

"""
Creates a somewhat random welcome message for the user to be displayed
"""
def create_welcome_message(username):
    general_greetings_list = ["hello", "hi", "welcome"]
    secondary_statement_list = ["hope you're having a great day!", "miao miao miao (that's cat for have a good day)!", "enjoy!", "good luck!", "happy writing!"]
    return random.choice(general_greetings_list) + " " + username.capitalize() + "! " + random.choice(secondary_statement_list)

"""
Format a parsed note into an understandable
plain text version for later download
"""
def reformat_for_export(parsed_note_data):
    export_string = "================================================================\n"
    export_string += "Title: " + parsed_note_data["title"] + "\n"
    export_string += "================================================================\n"
    export_string += "Date Created: " + parsed_note_data["ui_date"] + "\n"
    export_string += "Tags: " + ", ".join(parsed_note_data["tags"]) + "\n"
    export_string += "================================================================\n"
    export_string += "Note:\n" + parsed_note_data["content"] + "\n"
    return export_string