import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from models import *

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
db = SQLAlchemy(app)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/cards/")
def cards():
    card = Card("Test card", 0, True, "")
    print card
    return card

if __name__ == "__main__":
    print os.environ['APP_SETTINGS']
    app.run(debug=True)
