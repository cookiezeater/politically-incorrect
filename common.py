"""
    common
    ~~~~~
    Config setup and app variables for importing.
"""

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from config import (
    Production,
    Development,
    Testing
)


app = Flask(__name__)
db  = SQLAlchemy(app)
log = app.logger
