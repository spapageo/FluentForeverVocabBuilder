#!/usr/bin/env bash

source venv/bin/activate && export FLASK_DEBUG=1 && export FLASK_ENV=DEVELOPMENT && export FLASK_APP=ff.py && flask run --port 8080 --host 0.0.0.0
