import os

from flask import Flask
from flask_bootstrap import Bootstrap
from app.service import web_driver
import atexit

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
app.config.from_pyfile('../settings.cfg')
app.config["web_driver"] = web_driver.WebDriver(app.config["TEMP_DIR"])

def cleanup(drv):
    drv.driver_cleanup()

atexit.register(cleanup, drv=app.config["web_driver"])

bootstrap = Bootstrap(app)

from app import routes

cfg = app.config


def setup_temp_dir():
    if not os.path.exists(cfg["TEMP_DIR"]):
        os.makedirs(os.path.join(os.getcwd(), cfg["TEMP_DIR"]))


def remove_temp_files():
    for r, dirs, files in os.walk(os.path.join(os.getcwd(), cfg["TEMP_DIR"]), topdown=False):
        for name in files:
            os.remove(os.path.join(r, name))
        for name in dirs:
            os.rmdir(os.path.join(r, name))


remove_temp_files()
setup_temp_dir()

