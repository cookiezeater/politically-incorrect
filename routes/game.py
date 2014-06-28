from routes.shared import *


@app.route("/matches/<int:match_id>/invite", methods=["POST"])
def invite_player(match_id):
    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.host_id == content["inviter"]
    match.pending.append(Player.query.get_or_404(content["invitee"]))
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


@app.route("/matches/<int:match_id>/accept", methods=["POST"])
def accept_invite(match_id):
    """
    First, assert that the acceptor is not
    the host of the match and the match is not full.
    Second, assert that the match is in the acceptor's
    list of invites. Then, remove the match from the list.
    Finally, create a state that links the match to
    the accepting player.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.host_id != content["acceptor_id"]
    print len(match.states)
    assert len(match.states) <= match.max_players
    acceptor = Player.query.get_or_404(content["acceptor_id"])
    assert match in acceptor.invited
    acceptor.invited.remove(match)
    state = State(acceptor.id, match.id)
    db.session.add(state)
    match.states.append(state)
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


def new_round(match):
    match.judge.judged += 1
    match.judge = min(match.states, key=lambda state: state.judged)
    for state in match.states:
        state.played_id = None
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


def round_ended(match):
    return all([states.played_id for states in match.states])


@app.route("/matches/<int:match_id>/begin", methods=["POST"])
def begin_match(match_id):
    """
    First, assert that the initiater is the host and
    there are a valid number of players. Second,
    remove all pending players. Then,
    set the game's status to 'ONGOING'.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.host_id == content["player_id"]
    assert 3 <= len(match.states) <= 10
    match.pending = []
    match.status = "ONGOING"
    match.judge = Player.query.get(
        id=random.randint(0, len(Player.query.all) - 1))
    db.session.add(match)
    db.session.commit()
    # @todo: distribute cards
    return new_round(match)


@app.route("/matches/<int:match_id>/go", methods=["POST"])
def next_turn(match_id):
    """
    Assert that the match is ongoing and that the player
    is in the game. Then, assert that the player has not already played
    a card for this round and the card is in the player's hand.
    Put down the card that the player has
    chosen. Add a card to the player's hand. Check if
    the round has ended.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.status == "ONGOING"
    assert content["player_id"] in [state.player_id for state in match.states]
    state = match.state.get(player_id=content["player_id"])
    assert not state.played_id
    card = Card.query.get(id=content["card_id"])
    assert card in state.hand
    state.played_id = card
    state.hand.add(Card.query.get(id=random.randint(0, 10))) # temporary
    db.session.add(match)
    db.session.add(state)
    db.session.commit()
    if round_ended(match):
        return new_round(match)
    else:
        return jsonify(status="success")
