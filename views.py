#!/usr/bin/env python

from app import app, db
from models import *
from flask import jsonify, request

@app.route("/")
def hello():
    return "Hello World!"

@app.route("/cards", methods=["GET"])
def get_all_cards():
    cards = Card.query.all()
    cards = {card.text: card.id for card in cards}
    return jsonify(**cards)

@app.route("/cards/<int:card_id>", methods=["GET"])
def get_card(card_id):
    card = Card.query.get(card_id)
    return jsonify(card=card.text)

@app.route("/cards", methods=["POST"])
def create_card():
    content = request.json

    card = Card(text=content["text"],
                rank=0,
                white=bool(content["white"]))
    db.session.add(card)
    db.session.commit()
    return jsonify(status="success")

@app.route("")

if __name__ == "__main__":
    db.create_all()
    app.run(debug=True, port=5000)
