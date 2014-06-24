#!/usr/bin/env python

from app import app
from models import *
from flask import jsonify, request

@app.route("/cards", methods=["GET"])
def get_all_cards():
    cards = Card.query.all()
    cards = {card.text: card.id for card in cards}
    return jsonify(**cards)

@app.route("/cards/<int:card_id>", methods=["GET"])
def get_card(card_id):
    card = Card.query.get(card_id)
    return jsonify(card=card.text, white=card.white)

@app.route("/cards/<int:card_id>", methods=["PUT"])
def update_card(card_id):
    card = Card.query.get(card_id)
    content = request.json
    card.text = content["text"]
    card.white = bool(content["white"])
    db.session.add(card)
    db.session.commit()
    return jsonify(status="success")

@app.route("/cards/<int:card_id>", methods=["DELETE"])
def delete_card(card_id):
    """
    This is unstable right now because
    deleting a card cascades to all the matches
    it was used in.
    """

    card = Card.query.get(card_id)
    db.session.delete(card)
    db.session.commit()
    return jsonify(status="success")

@app.route("/cards", methods=["POST"])
def create_card():
    content = request.json
    card = Card(content["text"],
                bool(content["white"]))
    db.session.add(card)
    db.session.commit()
    return jsonify(status="success")

@app.route("/users", methods=["POST"])
def create_user():
    content = request.json
    user = User(content["username"],
                content["email"],
                content["first_name"],
                content["last_name"])
    db.session.add(user)
    db.session.commit()
    return jsonify(status="success")

if __name__ == "__main__":
    db.create_all()
    app.run()
