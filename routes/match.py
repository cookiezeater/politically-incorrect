from routes.shared import *


@app.route("/matches", methods=["GET"])
def get_all_matches():
    matches = Match.query.all()
    matches_data = []
    for match in matches:
        match_data = {"id": match.id,
                      "name": match.name,
                      "host": match.host_id,
                      "max_players": match.max_players,
                      "max_score": match.max_score,
                      "match_status": match.status,
                      "winner": match.winner_id,
                      "deck_size": len(match.deck),
                      "black": None if not match.black_id
                               else Card.query.get_or_404(match.black_id).text}

        players = [Player.query.get_or_404(state.player_id)
                   for state in match.states]
        match_data["players"] = {player.id: {"first_name": player.first_name,
                                             "last_name": player.last_name,
                                             "username": player.username}
                                 for player in players}

        match_data["pending"] = {player.id: {"first_name": player.first_name,
                                         "last_name": player.last_name,
                                         "username": player.username}
                                 for player in match.pending}

        judge_query = State.query.filter_by(match_id=match.id, judge=True)
        match_data["judge"] = None if not judge_query.first() \
                              else judge_query.first().player_id

        matches_data.append(match_data)

    return jsonify(status="success", matches=matches_data)


@app.route("/matches/<int:match_id>", methods=["POST"])
def get_match(match_id):
    content = request.json
    match = Match.query.get_or_404(match_id)
    player = Player.query.get_or_404(content["player_id"])

    assert player.password == content["password"]

    player_is_playing = content["player_id"] in [state.player_id
                                                 for state in match.states]
    player_is_invited = match.id in [m.id for m in player.invited]

    assert player_is_playing or player_is_invited, \
           "You're not allowed to view this match."

    match_data = {"name": match.name,
                  "host": match.host_id,
                  "max_players": match.max_players,
                  "max_score": match.max_score,
                  "match_status": match.status,
                  "winner": match.winner_id,
                  "deck_size": len(match.deck),
                  "black": None if not match.black_id
                           else Card.query.get_or_404(match.black_id).text}

    players = [Player.query.get_or_404(state.player_id)
               for state in match.states]
    match_data["players"] = {player.id: {"first_name": player.first_name,
                                         "last_name": player.last_name,
                                         "username": player.username}
                             for player in players}
    for player in players:
        player_state = State.query.filter_by(player_id=player.id,
                                             match_id=match.id).first()
        match_data["players"][player.id]["played"] = \
                {card.id: card.text for card in player_state.played}
        match_data["players"][player.id]["hand"] = \
                {card.id: card.text for card in player_state.hand}

    match_data["pending"] = {player.id: {"first_name": player.first_name,
                                         "last_name": player.last_name,
                                         "username": player.username}
                             for player in match.pending}

    judge_query = State.query.filter_by(match_id=match.id, judge=True)
    match_data["judge"] = None if not judge_query.first() \
                          else judge_query.first().player_id

    return jsonify(status="success", **match_data)


@app.route("/matches", methods=["POST"])
def create_match():
    content = request.json
    player_id = content["player_id"]
    password = content["password"]
    name = content["name"]
    max_players = content["max_players"]
    max_score = content["max_score"]
    player = Player.query.get_or_404(player_id)
    assert player.password == password
    assert 3 <= max_players <= 10
    assert 5 <= max_score <= 20
    match = Match(name, player_id, max_players, max_score)
    state = State(player_id, match.id)
    db.session.add(state)
    match.states.append(state)
    match.deck = Card.query.all()  # temporary
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success", match_id=match.id)


@app.route("/matches/<int:match_id>", methods=["DELETE"])
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    db.session.delete(match)
    db.session.commit()
    return jsonify(status="success")
