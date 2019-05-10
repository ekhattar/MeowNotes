# MeowNotes

The note-taking app for cat lovers.

## About

MeowNotes is a Python-based web app written with [Flask](http://flask.pocoo.org/) and an [SQLite](https://www.sqlite.org/index.html) database.

Additionally, MeowNotes makes use of the following: [Bootstrap](https://getbootstrap.com/docs/4.3/getting-started/introduction/), [Font Awesome](https://fontawesome.com/), [Google Fonts](https://fonts.google.com/), and [Cat as a Service](https://cataas.com/#/).

(Planned) structure of this repo:

```bash
|--documentation    technical & product documentation
|--meownotes        main source code directory including SQLite db
|----static         assets for the flask app
|------css          custom & bootstrap css files
|------img          image assets for MeowNotes
|------js           custom & bootstrap + dependencies js files
|----templates      html templates for the flask app
```

## Prerequisites

- python3
- virtual env

```bash
pip3 install virtualenv
```

## Setup

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
```

## Start MeowNotes locally

Dev/debug mode (live reload on change)

```bash
# Start the virtual env
source venv/bin/activate
# Set env var to see extra debug output
export MEOWNOTES_DEBUG=True
# Start in debug mode (live reload on change)
python3 meownotes/__init__.py
```

"Production" mode

```bash
# Start the virtual env
source venv/bin/activate
# Start the app
export FLASK_APP=meownotes/__init__.py
flask run
```

See MeowNotes at [localhost:5000/](http://localhost:5000/)