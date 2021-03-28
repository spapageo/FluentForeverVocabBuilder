@echo off
cmd /k "venv\Scripts\activate & set FLASK_ENV=DEVELOPMENT & set FLASK_APP=ff.py & set FLASK_DEBUG=1 & flask run --port 8080 --host 0.0.0.0"
