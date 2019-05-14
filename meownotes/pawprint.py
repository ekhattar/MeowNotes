#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, session, flash, send_from_directory, url_for, send_file, Response, g, Blueprint
from werkzeug.security import check_password_hash, generate_password_hash
import random
import os
import sys

ROOT = os.path.dirname(os.path.realpath(__file__))

# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path

from dbquery import *
from utils import *

bp = Blueprint("pawprint", __name__)

# Landing page - either shows login/sign-up or redirects to dashboard
@bp.route("/")
def landing():
    if g.uid:
        return redirect("/dashboard")
    else:
        return render_template("landing.html", menu_item="login")

# Page that shows a random cat :)
@bp.route("/cat")
def cat():
    # append a random number to the end of the cat image url
    # to prevent caching (otherwise same photo always shown)
    cat = "https://cataas.com/cat" + "?" +str(random.randint(1,101))
    return render_template("/cat.html", cat=cat)

# Handles login and sign up before redirecting to the dashboard
@bp.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "GET":
        return redirect("/dashboard")
    else:
        # get the input username and password from the form
        input_username = request.form["username"]
        input_password = request.form["password"]
        # check that the fields are not empty somehow
        if not input_password or not input_password:
            msg = "The username or password were empty!"
            return render_template("landing.html", msg=msg)
        # check the db for existing users with the input username
        db_res = get_user_by_name(input_username)
        # if the user already exists, if the password is right then user logs in
        if (len(db_res) == 1):
            db_user = parse_user(db_res[0])
            # if the password is right then user logs in
            if check_password_hash(db_user["password"], input_password):
                # store the current user for the session
                session["username"] = input_username.lower()
                return redirect("/dashboard")
            # if the password is wrong, prompt to try again
            else:
                msg = "The password was wrong for the existing user. To make a new account, please enter a different username."
                return render_template("landing.html", msg=msg)
        else:
            # create the new user
            create_user(input_username, generate_password_hash(input_password))
            # store the new user for the session
            session["username"] = input_username.lower()
            return redirect("/dashboard")

# Dashboard - shows notes for the user
@bp.route("/dashboard")
def dashboard():
    if g.uid:
        session_user = g.username
        uid = g.uid
        # get the notes associated with the user
        db_user_results = get_notes_by_user(uid)
        note_data = process_note_results(db_user_results)
        # create the welcome message
        msg = create_welcome_message(session_user)
        return render_template("dashboard.html", msg=msg, menu_item="logout", data=note_data)
    return redirect("/")

# Log out button in menu - handles logout then redirects to landing page
@bp.route("/logout")
def logout():
    session.pop("username", None)
    session.clear()
    return redirect("/")

# Shows a note based on its id in single note view
@bp.route("/view")
def view():
    if g.uid:
        uid = g.uid
        # get the note id from the query string param
        requested_note_id = request.args.get("id")
        # retrieve note from the database
        db_note_results = get_note_by_id(uid, requested_note_id)
        note_data = process_note_results(db_note_results)
        return render_template("view.html", menu_item="logout", data=note_data[0])
    return redirect("/")

# Download as plain text file the contents of the note
@bp.route("/download")
def download():
    if g.uid:
        uid = g.uid
        # get the note id from the query string param
        requested_note_id = request.args.get("id")
        # retrieve note from the database
        db_note_results = get_note_by_id(uid, requested_note_id)
        note_data = reformat_for_export(process_note_results(db_note_results)[0])
        file_name = "note_" + str(requested_note_id) + ".txt"
        return Response(note_data,
                    mimetype="text/plain",
                    headers={"Content-Disposition":
                                    "attachment;filename=" + file_name})
    return redirect("/")

# Handle update of a note's contents (editing done from single note view)
@bp.route("/update", methods=("GET", "POST"))
def update():
    if request.method == "POST" and g.uid:
        uid = g.uid
        # get the note id and other data from the form
        note_id = request.form["note_id"]
        input_title = request.form["title"]
        input_tags = request.form["tags"]
        input_content = request.form["content"]
        update_note(uid, note_id, input_title, input_tags, input_content)
    return redirect("/dashboard")

# Create new note (can be done from the dashboard)
@bp.route("/create", methods=("GET", "POST"))
def create():
    if g.uid:
        # display the create page
        if request.method == "GET":
            return render_template("create.html", menu_item="logout")
        # save the note in the db for POST requests (from the form on the create page)
        else:
            uid = g.uid
            # get the form inputs
            input_title = request.form["title"]
            input_tags = request.form["tags"]
            input_content = request.form["content"]
            create_note(uid, input_title, input_tags, input_content)
            return redirect("/dashboard")
    return redirect("/")

# Delete a note (can be done from the dashboard, search results, or single view pages)
@bp.route("/delete", methods=("GET", "POST"))
def delete():
    if request.method == "POST" and g.uid:
        uid = g.uid
        # get the note id from the form POST request
        requested_note_id = request.form["note_id"]
        # delete note from the database
        delete_note_by_id(uid, requested_note_id)
    return redirect("/dashboard")

# Handle search (available only if logged in)
@bp.route("/search", methods=("GET", "POST"))
def search():
    if g.uid:
        # show search results
        if request.method == "POST":
            uid = g.uid
            # get the search term
            input_term = request.form["search"]
            # store the current search term
            session["search"] = input_term.lower()
            # retrieve notes from the database that match the search term
            db_search_results = get_search_notes(uid, input_term)
            note_data = process_note_results(db_search_results)
            num_results = len(note_data)
            return render_template("search.html", menu_item="logout", data=note_data, num=num_results, term=input_term)
        # show empty search page
        else:
            # clear the search term last stored
            session.pop("search", None)
            return render_template("search.html", menu_item="logout", data={}, num=0, term="(none, please use the search)")
    return redirect("/")

# Filters last search result by whatever was checked (done from search page)
@bp.route("/filter", methods=("GET", "POST"))
def filter():
    if g.uid:
        # show search results
        if request.method == "POST":
            uid = g.uid
            if session.get("search") is not None:
                last_search = session.get("search")
                input_fields = request.form.getlist("fields")
                # retrieve notes from the database that match the search term
                db_search_results = get_search_notes(uid, last_search, input_fields)
                note_data = process_note_results(db_search_results)
                num_results = len(note_data)
                return render_template("search.html", menu_item="logout", data=note_data, num=num_results, term=last_search)
            else:
                return redirect("/search")
        else:
            return redirect("/search")
    return redirect("/")

# make available for each request the uid and username of current user
@bp.before_app_request
def check_user_logged_in():
    if session.get("username") is not None:
        g.username = session.get("username")
        g.uid = get_id_by_user(session.get("username"))
    else:
        g.uid = None