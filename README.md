# MeowNotes

The note-taking app for cat lovers.

See live at: http://ekhattar.pythonanywhere.com/

## About

MeowNotes is a Python-based web app written with [Flask](http://flask.pocoo.org/) and an [SQLite](https://www.sqlite.org/index.html) database.

Additionally, MeowNotes makes use of the following: [Bootstrap](https://getbootstrap.com/docs/4.3/getting-started/introduction/), [Font Awesome](https://fontawesome.com/), [Google Fonts](https://fonts.google.com/), and [Cat as a Service](https://cataas.com/#/).

Structure of this repo:

```bash
|--documentation    basic documentation
|--meownotes        main source code directory including SQLite db
|----static         assets for the flask app
|------css          custom & bootstrap css files
|------img          image assets for MeowNotes
|------js           custom & bootstrap + dependencies js files
|----templates      html templates for the flask app
```

## Prerequisites

- python3
- virtualenv

```bash
pip3 install virtualenv
```
- recommended: [make](https://www.gnu.org/software/make/)
  - needed only if want to use the `Makefile` commands as shortcuts

## Setup

General setup

```bash
# Clone the repo
git clone https://github.com/ekhattar/MeowNotes.git
# Change directory
cd MeowNotes
# Create the virtual env
python3 -m venv venv
# Start the virtual env
source venv/bin/activate
# Install flask and other dependencies in the virtual env
pip install flask
pip install python-dateutil
# Optional: install if want to run with wsgi server locally
pip install uwsgi
```

(Re)create the database; __danger__, will delete existing contents and create new tables!

```bash
# Option 1: using make
make fresh-db
# Option 2: without using make
export FLASK_APP=meownotes
flask initdb
```

## Start MeowNotes locally

### Dev/debug mode 

This mode has live reload on change as well as additional logging output in the console including the prepared SQL queries and results; can use either `make` or "manually" run the necessary commands to start.

See MeowNotes at [localhost:5000/](http://localhost:5000/).

Start dev/debug mode with `make`:

```bash
# In the MeowNotes folder
make run-debug
```

Start manually:

```bash
# Start the virtual env
source venv/bin/activate
# Set env var to see extra debug output
export MEOWNOTES_DEBUG=True
# Start in debug mode (live reload on change)
python3 meownotes/__init__.py
```

### "Production" mode

This mode suppresses the additional logging output and starts on a different port.

See MeowNotes at [localhost:8000/](http://localhost:8000/).

Start with `make`:

```bash
# In the MeowNotes folder
make run-prod
```

Start manually:

```bash
# Start the virtual env
source venv/bin/activate
# Start the app
export FLASK_APP=meownotes/__init__.py
flask run
```

Using the wsgi server:

```bash
# In the MeowNotes folder
make run-wsgi
```

## Features

- __sign up / login__ (from the landing)
- __logout__ (from the menu bar)
- __view a random cat__ (from the menu bar)
- __create__ a new note with a title, tags, and content (from the dashboard)
- __edit__ an existing note (from the single note view)
- __delete__ an existing note (from the dashboard, search, or single note view)
- __download__ an existing note (from the single note view)
- __search__ for a note by its title, tags, and/or content (from the menu bar)
- __filter__ the search to limit to a specific field (from the search results page)

### Screenshots

#### Landing (login / sign-up)
![landing](documentation/screenshots/landing.png)

#### Dashboard
![dashboard](documentation/screenshots/dashboard.png)

#### Create a note
![create note](documentation/screenshots/create-note-view.png)

#### View a note
![view note](documentation/screenshots/single-note-view.png)

#### Edit a note
![edit note](documentation/screenshots/edit-note-view.png)

#### Downloaded note
![download(ed) note](documentation/screenshots/downloaded-file.png)

#### View a random cat
![random cat](documentation/screenshots/random-cat.png)

### Routes

- `/`
    - `GET` show the langing (login/sign-up page)
- `/cat`
    - `GET` show the cat page with a random cat
- `/login`
    - `GET` redirect to the dashboard if signed in
    - `POST` either login or create a new account; if password is wrong for an existing account, the landing page is rerendered with the warning message; if the password is right or a new account is created, redirect to the dashboard
- `/logout`
    - `GET` remove the username from the session and redirect to the landing
- `/dashboard`
    - `GET` show the dashboard page with the user's notes
- `/view`
    - `GET` show the view page for the given note by id
- `/download`
    - `GET` note data sent as raw text file to download
- `/update`
    - `GET` redirect to the dashboard
    - `POST` (DB) update the note with the given id from the form
- `/create`
    - `GET` show the create page
    - `POST` (DB) create a new note
- `/delete`
    - `GET` redirect to dashboard
    - `POST` (DB) delete the note with the given id from the form
- `/search`
    - GET: show empty search results page
    - POST: show populated search results
- `/filter`
    - GET: redirect to (empty) search results page
    - POST: render search results with filters applied

_Note_: all `GET` requests additionally to the above redirect to the landing (login page) if the user is not logged in

