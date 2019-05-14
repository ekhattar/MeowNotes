APP_DIR=meownotes
APP_ENTRY_POINT=__init__.py
MEOWNOTES_PORT=8000
MEOWNOTES_HOST="0.0.0.0"

run-debug:
	echo ">>> INFO: starting MeowNotes with debug mode enabled on default port 5000"
	export MEOWNOTES_DEBUG=True && python $(APP_DIR)/$(APP_ENTRY_POINT)

run-prod:
	echo ">>> INFO: starting MeowNotes with prod mode enabled on $(MEOWNOTES_HOST):$(MEOWNOTES_PORT)/"
	cd $(APP_DIR) && export PYTHONPATH=. && export FLASK_APP=$(APP_ENTRY_POINT) && export FLASK_RUN_HOST=$(MEOWNOTES_HOST)&& export FLASK_RUN_PORT=$(MEOWNOTES_PORT) && flask run

run-wsgi:
	export MEOWNOTES_LOCALDEV=True && uwsgi --socket $(MEOWNOTES_HOST):5000 --protocol=http -w wsgi:application