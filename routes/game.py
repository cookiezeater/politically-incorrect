from routes.shared import *
from random import randint


@app.route("/matches/<int:match_id>/invite", methods=["POST"])
def invite_player(match_id):
    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.host_id == content["inviter"]
    assert content["invitee"] not in [state.player_id for state in match.states]
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
    assert len(match.states) < match.max_players
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
    for state in match.states:
        if state.judge:
            old_judge = state
            old_judge.judged += 1
            db.session.add(old_judge)
    white_cards = filter(lambda card: card.white, match.deck)
    for state in match.states:
        state.played_id = None
        state.viewed_round_end = False
        state.judge = False
        if state.round_winner:
            state.score += 1
        state.round_winner = False
        while len(state.hand) < 10:
            state.hand.append(white_cards[randint(0, len(white_cards) - 1)])
        db.session.add(state)
    new_judge = min(match.states, key=lambda state: state.judged)
    new_judge.judge = True
    db.session.add(new_judge)
    black_cards = filter(lambda card: not card.white, match.deck)
    match.black_id = black_cards[randint(0, len(black_cards) - 1)].id
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

    @todo:
        - host can not be first judge (fix this glitch)
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.host_id == content["player_id"]
    assert 3 <= len(match.states) <= 10
    match.pending = []
    match.status = "ONGOING"
    match.judge = match.states[randint(0, match.max_players - 1)]
    db.session.add(match)
    db.session.commit()
    return new_round(match)


@app.route("/matches/<int:match_id>/go", methods=["POST"])
def make_move(match_id):
    """
    Assert that the match is ongoing and that the player
    is in the game. Then, assert that the player has not already played
    a card for this round and the card is in the player's hand.
    Put down the card that the player has chosen.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.status == "ONGOING"
    assert content["player_id"] in [state.player_id for state in match.states]
    state = match.state.get(player_id=content["player_id"])
    assert not state.played_id
    card = Card.query.get(content["card_id"])
    assert card in state.hand
    state.played_id = card
    db.session.add(match)
    db.session.add(state)
    db.session.commit()
    if round_ended(match):
        return jsonify(status="success")
    else:
        return jsonify(status="success")


@app.route("/matches/<int:match_id>/round_status", methods=["POST"])
def round_status(match_id):
    """Returns a list of who has played a card in the round."""

    content = request.json
    match = Match.query.get(match_id)
    assert content["player_id"] in [state.player_id for state in match.states]
    if all([state.viewed_round_end for state in match.states]):
        return jsonify(status="success", round_state="ended")
    return jsonify(status="success",
                   round_state="ongoing",
                   **{state.player_id: None if not state.played_id else
                      Card.query.get(state.played_id).text
                      for state in match.states})


@app.route("/matches/<int:match_id>/hand", methods=["POST"])
def hand(match_id):
    content = request.json
    match = Match.query.get(match_id)
    assert content["player_id"] in [state.player_id for state in match.states]
    state = State.query.filter_by(player_id=content["player_id"],
                                  match_id=match_id).first()
    return jsonify(hand=[card.text for card in state.hand])


@app.route("/matches/<int:match_id>/reveal", methods=["POST"])
def reveal_cards(match_id):
    """Return all the cards played for the round if the round has ended."""

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert content["player_id"] in [state.player_id for state in match.states]
    assert round_ended(match)
    return jsonify(status="success",
                   cards=[Card.query.get(state.played_id).text
                          for state in match.states])


@app.route("/matches/<int:match_id>/choose", methods=["POST"])
def choose_winner(match_id):
    """The judge chooses the winner."""

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert round_ended(match)
    assert content["judge_id"] != content["winner_id"]
    assert content["judge_id"] == match.judge_id
    assert content["winner_id"] in [state.player_id for state in match.states]
    winner = match.states.get(player_id=content["winner_id"])
    winner.round_winner = True
    db.session.add(winner)
    db.session.add()


@app.route("/matches/<int:match_id>/acknowledge", methods=["POST"])
def acknowledge(match_id):
    """
    At the end of the round, everyone must view the game before a
    new round begins.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert round_ended(match)
    assert content["player_id"] in [state.player_id for state in match.states]
    player = Player.query.get(content["player_id"])
    player.viewed_round_end = True
    db.session.add(viewed_round_end)
    db.session.commit()
    return jsonify(status=True)
