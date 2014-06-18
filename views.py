from flask import Flask
from models import *

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/cards/")
def cards():
    card = Card("Test card", 0, True, "")
    print card
    return card

if __name__ == "__main__":
    app.run(debug=True)
