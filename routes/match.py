from routes.shared import *


@app.route("/matches", methods=["GET"])
def get_all_matches():
    matches = Match.query.all()
    matches = {"matches":
                    [{"id": match.id,
                      "pending": [player.id for player in match.pending],
                      "states": [str(state) for state in match.states],
                      "status": match.status}
                      for match in matches]}
    return jsonify(**matches)


@app.route("/matches/<int:match_id>", methods=["GET"])
def get_match(match_id):
    match = Match.query.get(match_id)
    if match:
      return jsonify(id=match.id,
                     states=match.states,
                     status=match.status)
    else:
      return jsonify("Match not found with that id.")

@app.route("/matches", methods=["POST"])
def create_match():
    content = request.json
    player_id = content["player_id"]
    match = Match(player_id)
    state = State(player_id, match.id)
    db.session.add(state)
    match.states.append(state)
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")
