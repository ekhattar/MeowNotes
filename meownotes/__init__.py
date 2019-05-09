#!/usr/bin/env python3
from flask import Flask, request, redirect, render_template, session, flash, send_from_directory, url_for, send_file
import random
from dbquery import *
from utils import *

app = Flask(__name__)

# Load the config
app.config.from_object("config.Config")

# Landing page - either shows login/sign-up or redirects to dashboard
@app.route("/")
def landing():
    if session.get("username") is not None:
        return redirect("/dashboard")
    else:
        return render_template("landing.html", menu_item="login")

# Page that shows a random cat :)
@app.route("/cat")
def cat():
    # append a random number to the end of the cat image url
    # to prevent caching (otherwise same photo always shown)
    cat = "https://cataas.com/cat" + "?" +str(random.randint(1,101))
    return render_template("/cat.html", cat=cat)

# Handles login and sign up before redirecting to the dashboard
@app.route("/login", methods=("GET", "POST"))
def login():
    if request.method == "GET":
        if session.get("username") is not None:
            return redirect("/dashboard")
        else:
            return redirect("/")
    else:
        # get the input username and password from the form
        input_username = request.form["username"]
        input_password = request.form["password"]
        # check the db for existing users with the input username
        db_res = get_user_by_name(input_username)
        # if the user already exists, if the password is right then user logs in
        if (len(db_res) == 1):
            db_user = parse_user(db_res[0])
            # if the password is right then user logs in
            if db_user["password"] == input_password:
                # store the current user for the session
                session["username"] = input_username.lower()
                return redirect("/dashboard")
            # if the password is wrong, prompt to try again
            else:
                msg = "The password was wrong for the existing user. To make a new account, please enter a different username."
                return render_template("landing.html", msg=msg)
        else:
            # create the new user
            create_user(input_username, input_password)
            # store the new user for the session
            session["username"] = input_username.lower()
            return redirect("/dashboard")

# Dashboard - shows notes for the user
@app.route("/dashboard")
def dashboard():
    if session.get("username") is not None:
        session_user = session.get("username")
        uid = get_id_by_user(session.get("username"))
        # get the notes associated with the user
        db_user_results = get_notes_by_user(uid)
        note_data = process_note_results(db_user_results)
        # create the welcome message
        msg = create_welcome_message(session_user)
        return render_template("dashboard.html", msg=msg, menu_item="logout", data=note_data)
    else:
        return redirect("/")

# Log out button in menu - handles logout then redirects to landing page
@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/")

# Shows a note based on its id in single note view
@app.route("/view")
def view():
    if session.get("username") is not None:
        uid = get_id_by_user(session.get("username"))
        # get the note id from the query string param
        requested_note_id = request.args.get("id")
        # retrieve note from the database
        db_note_results = get_note_by_id(uid, requested_note_id)
        note_data = process_note_results(db_note_results)
        return render_template("view.html", menu_item="logout", data=note_data[0])
    else:
        return redirect("/")

# Handle update of a note's contents (editing done from single note view)
@app.route("/update", methods=("GET", "POST"))
def update():
    if session.get("username") is not None:
        if request.method == "POST":
            uid = get_id_by_user(session.get("username"))
            # get the note id and other data from the form
            note_id = request.form["note_id"]
            input_title = request.form["title"]
            input_tags = request.form["tags"]
            input_content = request.form["content"]
            update_note(uid, note_id, input_title, input_tags, input_content)
        return redirect("/dashboard")
    else:
        return redirect("/")


# Create new note (can be done from the dashboard)
@app.route("/create", methods=("GET", "POST"))
def create():
    # display the create page
    if request.method == "GET":
        if session.get("username") is not None:
            return render_template("create.html", menu_item="logout")
        else:
            return redirect("/")
    # save the note in the db for POST requests (from the form on the create page)
    else:
        if session.get("username") is not None:
            uid = get_id_by_user(session.get("username"))
            # get the form inputs
            input_title = request.form["title"]
            input_tags = request.form["tags"]
            input_content = request.form["content"]
            create_note(uid, input_title, input_tags, input_content)
            return redirect("/dashboard")
        else:
            return redirect("/")

# Delete a note (can be done from the dashboard or search results pages)
@app.route("/delete", methods=("GET", "POST"))
def delete():
    if session.get("username") is not None:
        if request.method == "POST":
            uid = get_id_by_user(session.get("username"))
            # get the note id from the form POST request
            requested_note_id = request.form["note_id"]
            # delete note from the database
            delete_note_by_id(uid, requested_note_id)
        return redirect("/dashboard")
    else:
        return redirect("/")

# Handle search (available only if logged in)
@app.route("/search", methods=("GET", "POST"))
def search():
    if session.get("username") is not None:
        # show search results
        if request.method == "POST":
            uid = get_id_by_user(session["username"])
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
            return render_template("search.html", menu_item="logout", data={}, num=0)
    else:
        return redirect("/")

# Filters last search result by whatever was checked (done from search page)
@app.route("/filter", methods=("GET", "POST"))
def filter():
    if session.get("username") is not None:
        # show search results
        if request.method == "POST":
            uid = get_id_by_user(session["username"])
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
    else:
        return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
