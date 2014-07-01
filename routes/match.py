from routes.shared import *


@app.route("/matches", methods=["GET"])
def get_all_matches():
    matches = Match.query.all()
    matches_data = []
    for match in matches:
        match_data = {"id": match.id,
                      "host": match.host_id,
                      "max_players": match.max_players,
                      "match_status": match.status,
                      "states": [str(state) for state in match.states],
                      "pending": [player.id for player in match.pending],
                      "winner": match.winner_id,
                      "deck": [card.text for card in match.deck],
                      "black": None if not match.black_id
                               else Card.query.get(match.black_id).text}
        judge_query = State.query.filter_by(match_id=match.id, judge=True)
        match_data["judge"] = None if not judge_query.first() \
                              else judge_query.first().player_id
        matches_data.append(match_data)
    return jsonify(status="success", matches=matches_data)


@app.route("/matches/<int:match_id>", methods=["POST"])
def get_match(match_id):
    content = request.json
    match = Match.query.get_or_404(match_id)
    assert content["player_id"] in [state.player_id for state in match.states]
    match_data = {"id": match.id,
                  "host": match.host_id,
                  "max_players": match.max_players,
                  "match_status": match.status,
                  "states": [str(state) for state in match.states],
                  "pending": [player.id for player in match.pending],
                  "winner": match.winner_id,
                  "deck": [card.text for card in match.deck],
                  "black": None if not match.black_id
                           else Card.query.get(match.black_id).text}
    judge_query = State.query.filter_by(match_id=match.id, judge=True)
    match_data["judge"] = None if not judge_query.first() \
                          else judge_query.first().player_id
    return jsonify(status="success", **match_data)


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
