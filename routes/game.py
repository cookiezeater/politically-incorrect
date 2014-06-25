from routes.shared import *

@app.route("/players/<int:player_id>", methods=["POST"])
def invite_player(player_id):
    content = request.json
    match = Match.query.get(content["match_id"])
    assert match.host_id != player_id
    match.pending.append(Player.query.get(player_id))
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")
