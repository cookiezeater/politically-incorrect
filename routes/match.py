from routes.shared import *


@app.route("/matches", methods=["POST"])
@jsonify_assertion_error
@auth.login_required
def create_match():
    content = request.json
    name = content["name"]
    invites = content["invites"]
    max_players = content["max_players"]
    max_score = content["max_score"]
    assert 1 <= len(name) <= 30, \
           "Invalid game title."
    assert 3 <= max_players <= 10, \
           "Invalid number of players. (must be between 3 and 5)"
    assert 5 <= max_score <= 20, \
           "Invalid max score. (must be between 5 and 20)"
    match = Match(name, g.player.id, max_players, max_score)
    state = State(g.player.id, match.id)
    db.session.add(state)
    match.states.append(state)
    match.deck = Card.query.all()

    for email in invites:
        match.pending.append(get_player(email))

    db.session.add(match)
    db.session.commit()
    return jsonify(status="success", id=match.id)


@app.route("/matches/<int:match_id>", methods=["DELETE"])
@jsonify_assertion_error
@auth.login_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    assert match.host_id == g.player.id, \
           "You aren't allowed to delete this match."
    db.session.delete(match)
    db.session.commit()
    return jsonify(status="success")
