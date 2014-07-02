from routes.shared import *


@app.route("/cards", methods=["GET"])
def get_all_cards():
    cards = Card.query.all()
    white = {card.id: card.text for card in cards if card.white}
    black = {card.id: {"text": card.text, "answers": card.answers}
             for card in cards if not card.white}
    return jsonify(status="success", white=white, black=black)


@app.route("/cards/<int:card_id>", methods=["GET"])
def get_card(card_id):
    card = Card.query.get_or_404(card_id)
    return jsonify(status="success", card=card.text, white=card.white)


@app.route("/cards/<int:card_id>", methods=["PUT"])
def update_card(card_id):
    card = Card.query.get_or_404(card_id)
    content = request.json
    if "text" in content:
        card.text = content["text"]
    if "white" in content:
        card.white = content["white"]
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

    card = Card.query.get_or_404(card_id)
    db.session.delete(card)
    db.session.commit()
    return jsonify(status="success")


@app.route("/cards", methods=["POST"])
def create_card():
    content = request.json
    assert (content["white"] and "answers" not in content) or \
           (not content["white"] and "answers" in content)
    if content["white"]:
        card = Card(content["text"],
                    content["white"])
    else:
        card = Card(content["text"],
                    content["white"],
                    content["answers"])
    db.session.add(card)
    db.session.commit()
    return jsonify(status="success")
