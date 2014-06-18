from app import app, db
from models import *
from flask import jsonify

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/cards/")
def cards():
    cards = Card.query.all()
    cards = {card.text: "white" if card.white else "black" for card in cards}
    return jsonify(**cards)

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
