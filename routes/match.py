from routes.shared import *


@jsonify_assertion_error
@app.route("/matches", methods=["POST"])
@auth.login_required
def create_match():
    content = request.json
    name = content["name"]
    max_players = content["max_players"]
    max_score = content["max_score"]
    assert 3 <= max_players <= 10
    assert 5 <= max_score <= 20
    match = Match(name, g.player.id, max_players, max_score)
    state = State(g.player.id, match.id)
    db.session.add(state)
    match.states.append(state)
    match.deck = Card.query.all()  # temporary
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success", id=match.id)


@jsonify_assertion_error
@app.route("/matches/<int:match_id>", methods=["DELETE"])
@auth.login_required
def delete_match(match_id):
    match = Match.query.get_or_404(match_id)
    assert match.host_id == g.player.id, \
           "You aren't allowed to delete this match."
    db.session.delete(match)
    db.session.commit()
    return jsonify(status="success")
