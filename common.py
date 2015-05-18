"""
    Logging setup and app variables for importing.
    ~~~~~
    Logs on all levels to stdout and
    a log file. Contains original app and db
    objects for other files to import.
"""

import os
import sys
import logging
from flask import Flask, abort
from flask.ext.sqlalchemy import SQLAlchemy

app    = Flask(__name__)
config = os.environ["APP_SETTINGS"]

app.logger.info(config)
app.config.from_object(config)

db = SQLAlchemy(app)

file_handler = logging.FileHandler("pol.log")
file_handler.setLevel(logging.DEBUG)

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.DEBUG)

app.logger.addHandler(file_handler)
app.logger.addHandler(stdout_handler)

werkzeug_logger = logging.getLogger("werkzeug")
werkzeug_logger.setLevel(logging.DEBUG)

werkzeug_logger.addHandler(file_handler)
werkzeug_logger.addHandler(stdout_handler)

@app.errorhandler(500)
def internal_error(exception):
    app.logger.exception(exception)
    return Response("Something went horribly wrong..."), 500
