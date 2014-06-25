from routes.shared import *


@app.route("/matches/<int:match_id>/invite", methods=["POST"])
def invite_player(match_id):
    content = request.json
    match = Match.query.get(match_id)
    assert match.host_id == content["inviter"]
    match.pending.append(Player.query.get(content["invitee"]))
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


@app.route("/matches/<int:match_id>/accept", methods=["POST"])
def accept_invite(match_id):
    """
    Accept an invite. First, assert that the acceptor is not
    the host of the match. Second, assert that the match
    is in the acceptor's list of invites. Then, remove
    the match from the list. Finally, create a state that
    links the match to the accepting player.
    """

    content = request.json
    match = Match.query.get(match_id)
    assert match.host_id != content["acceptor_id"]
    acceptor = Player.query.get(content["acceptor_id"])
    print acceptor.invited
    assert match in acceptor.invited
    acceptor.invited.remove(match)
    state = State(acceptor.id, match.id)
    db.session.add(state)
    match.states.append(state)
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")
