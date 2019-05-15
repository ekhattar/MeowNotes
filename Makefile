APP_DIR=meownotes
APP_ENTRY_POINT=__init__.py
MEOWNOTES_PORT=8000
MEOWNOTES_HOST=0.0.0.0
VENV_DIR=venv

install:
	echo ">>> INFO: setting up MeowNotes environment"
	python3 -m venv $(VENV_DIR) && \
	source $(VENV_DIR)/bin/activate && \
	pip install flask && \
	pip install python-dateutil && \
	pip install uwsgi && \
	pip install pytest

fresh-db:
	echo ">>> INFO: (re)creating MeowNotes database"
	export FLASK_APP=$(APP_DIR) && \
	flask initdb

run-debug:
	echo ">>> INFO: starting MeowNotes with debug mode enabled on default port 5000"
	source $(VENV_DIR)/bin/activate && \
	export MEOWNOTES_DEBUG=True && \
	python $(APP_DIR)/$(APP_ENTRY_POINT)

run-prod:
	echo ">>> INFO: starting MeowNotes with prod mode enabled on $(MEOWNOTES_HOST):$(MEOWNOTES_PORT)/"
	source $(VENV_DIR)/bin/activate && \
	export FLASK_APP=$(APP_DIR) && \
	export FLASK_RUN_HOST=$(MEOWNOTES_HOST) && \
	export FLASK_RUN_PORT=$(MEOWNOTES_PORT) && \
	flask run

run-wsgi:
	echo ">>> INFO: starting MeowNotes using uWSGI on $(MEOWNOTES_HOST):$(MEOWNOTES_PORT)/"
	source $(VENV_DIR)/bin/activate && \
	export MEOWNOTES_LOCALDEV=True && \
	uwsgi --socket $(MEOWNOTES_HOST):$(MEOWNOTES_PORT) --protocol=http -w wsgi:application

test:
	source $(VENV_DIR)/bin/activate && \
	pytest
