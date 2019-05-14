APP_DIR=meownotes
APP_ENTRY_POINT=__init__.py
MEOWNOTES_PORT=8000
MEOWNOTES_HOST="0.0.0.0"

fresh-db:
	export FLASK_APP=$(APP_DIR) && flask initdb

run-debug:
	echo ">>> INFO: starting MeowNotes with debug mode enabled on default port 5000"
	export MEOWNOTES_DEBUG=True && python $(APP_DIR)/$(APP_ENTRY_POINT)

run-prod:
	echo ">>> INFO: starting MeowNotes with prod mode enabled on $(MEOWNOTES_HOST):$(MEOWNOTES_PORT)/"
	export FLASK_APP=$(APP_DIR) && export FLASK_RUN_HOST=$(MEOWNOTES_HOST) && export FLASK_RUN_PORT=$(MEOWNOTES_PORT) && flask run

run-wsgi:
	export MEOWNOTES_LOCALDEV=True && uwsgi --socket $(MEOWNOTES_HOST):$(MEOWNOTES_PORT) --protocol=http -w wsgi:application
