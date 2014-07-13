from routes.shared import *
from random import randint


def new_round(match):
    """Prepares a new round.

    This function is called at the initial
    game start and at the start of a new round. First, if
    there was a judge, increase his judged count. Next,
    remove each state's played card(s) (played), reset
    viewed_round_end, remove all judges, and fill up each
    state's hand. Then, choose a new judge by finding the
    first state who has judged the least so far. Finally,
    play a black card.
    """

    # Find the current judge and increment his judged count
    old_judge = State.query.filter_by(match_id=match_id, judge=True).first()
    old_judge.judged += 1
    db.session.add(old_judge)

    cards_to_remove = []
    white_cards = filter(lambda card: card.white, match.deck)

    # Prepare each state for a new round by removing
    # all cards from the table (played), resetting
    # acknowledgement of round end (viewed_round_end),
    # and removing all judges and round winners.
    for state in match.states:
        state.played = []
        state.viewed_round_end = False
        state.judge = False
        state.round_winner = False

        # Fill the state's hand and remove each drawn card from
        # the white_cards list to avoid duplicates. Add each
        # drawn card to cards_to_remove, which will be a list
        # of cards removed from the deck at the end of the function.
        while len(state.hand) < 10:
            draw_card = white_cards[randint(0, len(white_cards) - 1)]
            state.hand.append(draw_card)
            cards_to_remove.append(draw_card)
            white_cards.remove(draw_card)
        db.session.add(state)

    # Select a new judge by finding the
    # state which has the lowest judged count.
    new_judge = min(match.states, key=lambda state: state.judged)
    new_judge.judge = True

    # Randomly select a black card and have
    # the new judge put it on the table. Add
    # the black card to the list of cards to be removed.
    black_cards = filter(lambda card: not card.white, match.deck)
    black_card = black_cards[randint(0, len(black_cards) - 1)]
    match.black_id = black_card.id
    new_judge.played.append(black_card)
    cards_to_remove.append(black_card)

    # Remove all drawn cards from the deck.
    for card in cards_to_remove:
        match.deck.remove(card)

    db.session.add(new_judge)
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


def begin_match(match):
    """Starts a new match.

    Remove all pending players and
    set the game's status to 'ONGOING'.
    Begin a new round.
    """

    match.pending = []
    match.status = "ONGOING"
    db.session.add(match)
    db.session.commit()
    return new_round(match)


def all_cards_down(match):
    """True if all states have played a card."""
    return all([states.played for states in match.states])


def any_cards_down(match):
    """True if any cards have been played (including black)."""
    return any([state.played for state in match.states])


def all_viewed_round_end(match):
    """True if everyone has viewed the round end."""
    return all([state.viewed_round_end for state in match.states])


@catch_assertion_error
@app.route("/matches/<int:match_id>/invite", methods=["POST"])
def invite_player(match_id):
    """Sends an invite to a player for a match.

    Checks that the inviter is the host (only the host can invite),
    that the host has not invited himself,
    that the game is in the PENDING state,
    and that the invitee has not already been invited
    and is not in the game already. If all assertions pass,
    the invitee is added to the match's pending list.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    inviter_id = content["inviter_id"]
    invitee_id = content["invitee_id"]
    inviter = Player.query.get_or_404(inviter_id)
    assert invite.password == content["password"]
    assert match.host_id == inviter_id, "Only the host can invite!"
    assert inviter_id != invitee_id, "You can't invite yourself!"
    assert match.status == "PENDING", "The match has already started."
    assert invitee_id not in [player.id for player in match.pending], \
           "You already have an invite!"
    assert invitee_id not in [state.player_id for state in match.states], \
           "You're already in the match!"
    match.pending.append(Player.query.get_or_404(invitee_id))
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


@catch_assertion_error
@app.route("/matches/<int:match_id>/accept", methods=["POST"])
def accept_invite(match_id):
    """Accepts an invite to a match.

    Assert that the acceptor is not
    the host of the match. Assert the match is not full.
    Assert that the match is in the acceptor's
    list of invites. Then, remove the match from the acceptor's
    list of invites. Finally, create a state that links the match to
    the accepting player.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    acceptor_id = content["acceptor_id"]
    assert match.host_id != acceptor_id, "You're already in the match!"
    assert len(match.states) < match.max_players, "The match is full."
    acceptor = Player.query.get_or_404(acceptor_id)
    assert match in acceptor.invited, "You haven't been invited to this match."
    acceptor.invited.remove(match)
    state = State(acceptor.id, match.id)
    match.states.append(state)
    db.session.add(acceptor)
    db.session.add(state)
    db.session.add(match)
    db.session.commit()
    if len(match.states) == match.max_players:
        return begin_match(match)
    return jsonify(status="success")


@catch_assertion_error
@app.route("/matches/<int:match_id>/go", methods=["POST"])
def make_move(match_id):
    """Makes a move in a certain match for a player.

    Assert that the match is ongoing and the player
    is not the judge. Assert the player is in the game.
    Then, assert that the player has not already played
    a card/cards for this round, and the card(s) being played
    is in the player's hand. Put down the cards and remove
    them from the player's hand.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert match.status == "ONGOING"
    judge = State.query.filter_by(match_id=match_id,
                                  judge=True).first()
    assert content["player_id"] != judge.player_id
    assert content["player_id"] in [state.player_id for state in match.states]
    state = State.query.filter_by(player_id=content["player_id"],
                                  match_id=match_id).first()
    assert not state.played
    assert len(content["cards"]) == judge.played[0].answers
    for card_id in content["cards"]:
        card = Card.query.get_or_404(card_id)
        assert card in state.hand
        state.played.append(card)
        state.hand.remove(card)
    db.session.add(match)
    db.session.add(state)
    db.session.commit()
    return jsonify(status="success")


@catch_assertion_error
@app.route("/matches/<int:match_id>/round", methods=["POST"])
def round(match_id):
    """Returns information about the current round.

    First, assert that the player requesting information is part
    of the match. Then, grab round and match info as necessary
    and return it.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert content["player_id"] in [state.player_id for state in match.states]

    # Get round state
    if all_viewed_round_end(match):
        round_status = "ended"
    elif all_cards_down(match):
        round_status = "judging"
    elif any_cards_down(match):
        round_status = "ongoing"
    else:
        round_status = None

    # Get round winner, if he exists
    try:
        round_winner = State.query.filter_by(match_id=match_id,
                                             round_winner=True) \
                                            .first().player_id
    except:
        round_winner = None

    # Get round judge
    judge_id = State.query.filter_by(match_id=match_id,
                                     judge=True).first().player_id

    # Get all cards on the table as
    # {player_id: [(card_id, card_text), ...], ...}
    # and every player's hand as
    # {player_id: {card_id: card_text, ...}, ...}.
    # Cards played by the player (on the table) are
    # stored as a list of dictionaries because
    # order must be preserved.
    # Some black cards expect ordered answers.
    played, hands = {}, {}
    for state in match.states:
        played[str(state.player_id)] = [{str(card.id): card.text}
                                        for card in state.played]
        hands[str(state.player_id)] = {str(card.id): card.text
                                       for card in state.hand}

    # Get the number of required white cards to be played per player
    answers = Card.query.get_or_404(match.black_id).answers

    # Get each player's score
    scores = {state.player_id: state.score for state in match.states}

    return jsonify(status="success",
                   round_status=round_status,
                   round_winner=round_winner,
                   judge_id=judge_id,
                   played=played,
                   hands=hands,
                   answers=answers,
                   scores=scores)


@catch_assertion_error
@app.route("/matches/<int:match_id>/choose", methods=["POST"])
def choose_round_winner(match_id):
    """Chooses a winner for the round.

    Assert that everyone has played a card. Then, check that
    the judge has not chosen himself to be the winner. Assert that
    the judge is indeed the actual judge of the match. Assert that
    the winner is in the game. Finally, assert that nobody else
    has already won the round. Set the winner's state's round_winner
    to True and increment the winner's score.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert all_cards_down(match)
    assert content["judge_id"] != content["winner_id"]
    judge = State.query.filter_by(player_id=content["judge_id"],
                                  match_id=match_id,
                                  judge=True).first()
    assert content["judge_id"] == judge.player_id
    assert content["winner_id"] in [state.player_id for state in match.states]
    assert all([not state.round_winner for state in match.states])
    winner = State.query.filter_by(player_id=content["winner_id"],
                                   match_id=match_id).first()
    winner.round_winner = True
    winner.score += 1
    judge.viewed_round_end = True
    if winner.score == match.max_score:
        match.winner_id = winner.id
        match.status = "ENDED"
        db.session.add(match)
    db.session.add(judge)
    db.session.add(winner)
    db.session.commit()
    if match.status == "ENDED":
        return jsonify(status="success",
                       match_status="ENDED",
                       winner=match.winner_id)
    return jsonify(status="success")


@catch_assertion_error
@app.route("/matches/<int:match_id>/acknowledge", methods=["POST"])
def acknowledge(match_id):
    """Acknowledges the end round state. Everyone must acknowledge
    the end of the round for a new round to begin.

    Assert that all the cards have been placed and that a
    winner has been chosen. Assert that the player requesting
    information is in the game. Assert that the player
    has not already acknowledged the round end. Mark the player
    as having seen the end of the round by setting viewed_round_end
    to True. Check if everyone has acknowledged the round end. If so,
    a new round will begin.
    """

    content = request.json
    match = Match.query.get_or_404(match_id)
    assert all_cards_down(match), "Not all players have put down cards."
    assert any([state.round_winner for state in match.states]), \
           "A winner has not been chosen yet."
    assert content["player_id"] in [state.player_id
                                    for state in match.states], \
           "You're not in this game!"
    state = State.query.filter_by(player_id=content["player_id"],
                                  match_id=match_id).first()
    assert not state.viewed_round_end, "The round is already over!"
    state.viewed_round_end = True
    db.session.add(state)
    db.session.commit()
    if all_viewed_round_end(match):
        return new_round(match)
    return jsonify(status="success")
