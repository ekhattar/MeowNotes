#!/usr/bin/env python3
"""
Main Blueprint for the MeowNotes Flask app
"""
import random
import os
import sys
from flask import request, redirect, render_template, session, Response, g, Blueprint, flash
from werkzeug.security import check_password_hash, generate_password_hash
ROOT = os.path.dirname(os.path.realpath(__file__))
# add the project directory to the sys.path
if ROOT not in sys.path:
    sys.path = [ROOT] + sys.path
from dbquery import get_user_by_name, get_id_by_user, parse_user, create_user, \
    get_note_by_id, get_notes_by_user, get_search_notes, process_note_results, \
    update_note, delete_note_by_id, create_note
from utils import create_welcome_message, reformat_for_export

MEOW_BP = Blueprint("pawprint", __name__)

@MEOW_BP.route("/")
def landing():
    """
    Landing page - either shows login/sign-up or redirects to dashboard
    """
    if g.uid:
        return redirect("/dashboard")
    else:
        return render_template("landing.html", menu_item="login")

@MEOW_BP.route("/cat")
def cat():
    """
    Page that shows a random cat :)
    """
    # clear any notifications if there were any
    session.pop("_flashes", None)
    # append a random number to the end of the cat image url
    # to prevent caching (otherwise same photo always shown)
    cat_url = "https://cataas.com/cat" + "?" + str(random.randint(1, 101))
    # based on the current user status, need to show login or logout in the menu
    if g.uid:
        menu_item = "logout"
    else:
        menu_item = "login"
    return render_template("/cat.html", cat=cat_url, menu_item=menu_item)

@MEOW_BP.route("/login", methods=("GET", "POST"))
def login():
    """
    Handles login and sign up before redirecting to the dashboard
    """
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
        if len(db_res) == 1:
            db_user = parse_user(db_res[0])
            # if the password is right then user logs in
            if check_password_hash(db_user["password"], input_password):
                # store the current user for the session
                session["username"] = input_username.lower()
                # clear any notifications if there were any
                session.pop("_flashes", None)
                return redirect("/dashboard")
            # if the password is wrong, prompt to try again
            else:
                msg = "To make a new account, please enter a different username."
                flash("wrong password", "error")
                return render_template("landing.html", msg=msg)
        else:
            # create the new user
            create_user(input_username, generate_password_hash(input_password))
            # store the new user for the session
            session["username"] = input_username.lower()
            return redirect("/dashboard")

@MEOW_BP.route("/dashboard")
def dashboard():
    """
    Dashboard - shows notes for the user
    """
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

@MEOW_BP.route("/logout")
def logout():
    """
    Log out button in menu - handles logout then redirects to landing page
    """
    session.pop("username", None)
    session.pop("_flashes", None)
    session.clear()
    return redirect("/")

@MEOW_BP.route("/view")
def view():
    """
    Shows a note based on its id in single note view
    """
    if g.uid:
        uid = g.uid
        # get the note id from the query string param
        if request.args.get("id"):
            # requested_note_id = request.args.get("id")
            session["last_note_id"] = request.args.get("id")
        # if the request didn't include a note id, check the last one
        requested_note_id = session.get("last_note_id")
        # retrieve note from the database
        db_note_results = get_note_by_id(uid, requested_note_id)
        note_data = process_note_results(db_note_results)
        # if the list is empty, redirect!
        if not note_data:
            # add warning in the menu bar
            flash("note not found", "error")
            return redirect("/dashboard")
        return render_template("view.html", menu_item="logout", data=note_data[0])
    return redirect("/")

@MEOW_BP.route("/download")
def download():
    """
    Download as plain text file the contents of the note
    """
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

@MEOW_BP.route("/update", methods=("GET", "POST"))
def update():
    """
    Handle update of a note's contents (editing done from single note view)
    """
    if request.method == "POST" and g.uid:
        uid = g.uid
        # get the note id and other data from the form
        note_id = request.form["note_id"]
        input_title = request.form["title"]
        input_tags = request.form["tags"]
        input_content = request.form["content"]
        update_note(uid, note_id, input_title, input_tags, input_content)
        # add notification in the menu bar
        flash("note updated", "info")
    return redirect("/view")

@MEOW_BP.route("/create", methods=("GET", "POST"))
def create():
    """
    Create new note (can be done from the dashboard)
    """
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
            # add notification in the menu bar
            flash("note created", "info")
            return redirect("/dashboard")
    return redirect("/")

@MEOW_BP.route("/delete", methods=("GET", "POST"))
def delete():
    """
    Delete a note (can be done from the dashboard,
    search results, or single view pages)
    """
    if request.method == "POST" and g.uid:
        uid = g.uid
        # get the note id from the form POST request
        requested_note_id = request.form["note_id"]
        # delete note from the database
        delete_note_by_id(uid, requested_note_id)
        flash("note deleted", "error")
    return redirect("/dashboard")

@MEOW_BP.route("/search", methods=("GET", "POST"))
def search():
    """
    Handle search (available only if logged in)
    """
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
            # default filters
            def_filters = ["title", "tags", "content"]
            return render_template("search.html",
                                   menu_item="logout",
                                   data=note_data,
                                   num=num_results,
                                   term=input_term,
                                   filters=def_filters)
        # show empty search page
        else:
            # clear the search term last stored
            session.pop("search", None)
            return render_template("search.html",
                                   menu_item="logout",
                                   data={},
                                   num=0,
                                   term="(none, please use the search in the menu)")
    return redirect("/")

@MEOW_BP.route("/filter", methods=("GET", "POST"))
def filter_search():
    """
    Filters last search result by whatever was checked
    (done from search page)
    """
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
                # show the checked fields
                return render_template("search.html",
                                       menu_item="logout",
                                       data=note_data,
                                       num=num_results,
                                       term=last_search,
                                       filters=input_fields)
            else:
                return redirect("/search")
        else:
            return redirect("/search")
    return redirect("/")

@MEOW_BP.route("/clear")
def clear_messages():
    """
    Clears any active messages
    from flask flash then redirects back
    """
    session.pop("_flashes", None)
    return redirect(request.referrer)

@MEOW_BP.before_app_request
def check_user_logged_in():
    """
    Make available for each request
    the uid and username of current user
    """
    if session.get("username") is not None:
        g.username = session.get("username")
        g.uid = get_id_by_user(session.get("username"))
    else:
        g.uid = None
