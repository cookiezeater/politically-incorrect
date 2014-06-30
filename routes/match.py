from routes.shared import *


@app.route("/matches", methods=["GET"])
def get_all_matches():
    matches = Match.query.all()
    return jsonify(**{"matches":
                      [{"id": match.id,
                        "host": match.host_id,
                        "max_players": match.max_players,
                        "status": match.status,
                        "states": [str(state) for state in match.states],
                        "pending": [player.id for player in match.pending],
                        "winner": match.winner_id,
                        "judge": State.query.filter_by(match_id=match.id,
                                                       judge=True)
                                                      .first().player_id,
                        "deck": [card.text for card in match.deck],
                        "black": Card.query.get(match.black_id).text}
                       for match in matches]})


@app.route("/matches/<int:match_id>", methods=["GET"])
def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    return jsonify(id=match.id,
                   states=match.states,
                   status=match.status)


@app.route("/matches", methods=["POST"])
def create_match():
    content = request.json
    player_id = content["player_id"]
    max_players = content["max_players"]
    assert 3 <= max_players <= 10
    match = Match(player_id, max_players)
    state = State(player_id, match.id)
    db.session.add(state)
    match.states.append(state)
    match.deck = Card.query.all()  # temporary
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


@app.route("/matches/<int:match_id>", methods=["DELETE"])
def delete_match(match_id):
    match = Match.query.get(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify(status="success")
