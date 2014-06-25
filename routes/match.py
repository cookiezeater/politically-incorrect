from routes.shared import *


@app.route("/matches", methods=["GET"])
def get_all_matches():
    matches = Match.query.all()
    matches = {"matches":
                    [{"id": match.id,
                      "players": match.players,
                      "states": [str(state) for state in match.states],
                      "status": match.status}
                      for match in matches]}
    return jsonify(**matches)


@app.route("/matches/<int:match_id>", methods=["GET"])
def get_match(match_id):
    match = Match.query.get(match_id)
    return jsonify(id=match.id,
                   players=match.players,
                   states=match.states,
                   status=match.status)


@app.route("/matches", methods=["POST"])
def create_match():
    content = request.json
    player_id = int(content["player_id"])
    match = Match(player_id)
    state = State(player_id, match.id)
    db.session.add(state)
    match.states.append(state)
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")
