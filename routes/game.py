from routes.shared import *
from random import randint


def get_match_info(match, player=None, state=None):
    """Returns information about the match."""

    round_status = get_round_status(match)

    # Get round winner username, if any
    try:
        round_winner_id = get_round_winner_state(match.id).player_id
        round_winner = Player.query.get(round_winner_id).username
    except AttributeError:
        round_winner = None

    # Get match winner username
    try:
        match_winner = Player.query.get(match.winner_id).username
    except:
        match_winner = None

    # Get host username
    try:
        host = Player.query.get(match.host_id).username
    except:
        host = None

    # Get judge username, if any
    try:
        judge_id = get_judge_state(match.id).player_id
        judge = Player.query.get(judge_id).username
    except AttributeError:
        judge = None

    # Get the black card
    if match.black_id:
        black = Card.query.get(match.black_id)
        black_card = {"text": black.text, "answers": black.answers}
    else:
        black_card = None

    players, player_played_cards = get_players_as_json(match, player)

    # Get pending players from match relationship
    pending_players = [{"first_name": _.first_name,
                        "last_name": _.last_name,
                        "username": _.username}
                       for _ in match.pending]

    # Delete the previous round's previous round, if it exists
    if match.previous_round:
        if "previous_round" in match.previous_round:
            del match.previous_round["previous_round"]

    # Everything so far
    info = {"match_name": match.name,
            "match_status": match.status,
            "round_status": round_status,
            "max_players": match.max_players,
            "max_score": match.max_score,
            "round_winner": round_winner,
            "match_winner": match_winner,
            "host": host,
            "judge": judge,
            "black_card": black_card,
            "players": players,
            "pending_players": pending_players,
            "previous_round": match.previous_round}

    # Add player hand and played cards, if possible
    if player and state:
        # Get the requesting player's hand
        player_state = next(state for state in match.states
                            if state.player_id == player.id)
        hand = [{"id": card.id, "text": card.text}
                for card in player_state.hand]

        info["hand"] = hand
        info["played_cards"] = player_played_cards

    return info


def new_round(match):
    """Prepares a new round.

    This function is called at the initial
    game start and at the start of a new round. First,
    serialize and store the entirety of the previous
    round. If there was a judge, increase his judged count.
    Then, reset the previous round winner. Next,
    remove each state's played card(s) (played), reset
    viewed_round_end, remove all judges, and fill up each
    state's hand. Then, choose a new judge by finding the
    first state who has judged the least so far. Finally,
    play a black card.
    """

    # Check if there is a previous round by checking
    # for a black card
    if match.black_id:
        match.previous_round = get_match_info(match)

    # Find the current judge and increment his judged count
    try:
        old_judge_state = get_judge_state(match.id)
        old_judge_state.judged += 1
        db.session.add(old_judge_state)
    except:
        # This just means that we are starting a new round
        # for the first time, so the query will return a
        # NoneType.
        pass

    # Clear the round winner
    try:
        round_winner_state = get_round_winner_state(match.id)
        round_winner_state.round_winner = False
        db.session.add(round_winner_state)
    except:
        pass

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
    db.session.add(new_judge)

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


def get_round_status(match):
    """Determine round status."""
    if all_viewed_round_end(match):
        return "ended"
    elif all_cards_down(match):
        return "judging"
    elif any_cards_down(match):
        return "ongoing"
    else:
        return None


def get_players_as_json(match, player=None):
    """Create the representation of a player in a match as json.

    [{id: player.id,
      first_name: player.first_name,
      last_name: player.last_name,
      score: player_state.score,
      played_cards: [{id: card.id, text: card.text},
                    ...]
      },
    ...]
    """
    player_played_cards = []
    players = [Player.query.get_or_404(state.player_id)
               for state in match.states]
    # Easy stuff first
    json_players = [{"first_name": _.first_name,
                     "last_name": _.last_name,
                     "username": _.username}
                    for _ in players]
    # Add the player's played_cards from the player's match state
    for index, _ in enumerate(json_players):
        player_state = next(state for state in match.states
                            if state.player_id == players[index].id)
        played_cards = [{"id": card.id, "text": card.text}
                        for card in player_state.played]
        _["played_cards"] = played_cards
        _["score"] = player_state.score
        json_players[index] = _

        # For ease of access, store and return the requesting
        # player's played cards in the response
        if player and player_state.player_id == player.id:
            player_played_cards = played_cards

    return json_players, player_played_cards


def all_cards_down(match):
    """True if all states have played a card."""
    return all([states.played for states in match.states])


def any_cards_down(match):
    """True if any cards have been played (including black)."""
    return any([state.played for state in match.states])


def all_viewed_round_end(match):
    """True if everyone has viewed the round end."""
    return all([state.viewed_round_end for state in match.states])


@jsonify_assertion_error
@app.route("/matches", methods=["GET"])
@auth.login_required
def get_all_matches():
    matches = Match.query.all()
    return jsonify(status="success",
                   matches=[get_match_info(match) for match in matches])


@jsonify_assertion_error
@app.route("/matches/<int:match_id>", methods=["GET"])
@auth.login_required
def get_match_info_route(match_id):
    content = request.json
    match = Match.query.get_or_404(match_id)
    state = get_state(g.player.id, match.id)
    return jsonify(status="success", **get_match_info(match, g.player, state))


@jsonify_assertion_error
@app.route("/matches/<int:match_id>/invite", methods=["POST"])
@auth.login_required
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
    invitee = get_player(content["username"])
    match = Match.query.get_or_404(match_id)

    assert g.player.id == match.host_id, "Only the host can invite players!"
    assert g.player.id != invitee.id, "You can't invite yourself!"
    assert match.status == "PENDING", "The match has already started."
    assert invitee.id not in [player.id for player in match.pending], \
           "You already have an invite!"
    assert invitee.id not in [state.player_id for state in match.states], \
           "You're already in the match!"

    match.pending.append(invitee)
    db.session.add(match)
    db.session.commit()
    return jsonify(status="success")


@jsonify_assertion_error
@app.route("/matches/<int:match_id>/accept", methods=["GET"])
@auth.login_required
def accept_invite(match_id):
    """Accepts an invite to a match.

    Assert that the acceptor is not
    the host of the match. Assert the match is not full.
    Assert that the match is in the acceptor's
    list of invites. Then, remove the match from the acceptor's
    list of invites. Finally, create a state that links the match to
    the accepting player.
    """

    match = Match.query.get_or_404(match_id)

    assert match.host_id != g.player.id, "You're already in the match!"
    assert match in g.player.invited, "You haven't been invited to this match."
    assert len(match.states) < match.max_players, "The match is full."

    g.player.invited.remove(match)

    state = State(g.player.id, match.id)
    match.states.append(state)

    db.session.add(g.player)
    db.session.add(state)
    db.session.add(match)
    db.session.commit()

    if len(match.states) == match.max_players:
        return begin_match(match)
    return jsonify(status="success")


@jsonify_assertion_error
@app.route("/matches/<int:match_id>/go", methods=["POST"])
@auth.login_required
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
    assert match.status == "ONGOING", "The match isn't in progress."

    judge_state = get_judge_state(match.id)
    assert g.player.id != judge_state.player_id, \
           "You can't play a card because you're the judge this round."

    state = get_state(g.player.id, match.id)
    assert not state.played, \
           "You've already played your card(s) for this round."

    answers = judge_state.played[0].answers
    assert len(content["cards"]) == answers, \
           "You need to play {} cards this round.".format(answers)

    for card_id in content["cards"]:
        card = Card.query.get_or_404(card_id)
        assert card in state.hand
        state.played.append(card)
        state.hand.remove(card)

    db.session.add(match)
    db.session.add(state)
    db.session.commit()
    return jsonify(status="success")


@jsonify_assertion_error
@app.route("/matches/<int:match_id>/choose", methods=["POST"])
@auth.login_required
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

    judge_state = get_judge_state(match.id)
    judge_state.viewed_round_end = True

    assert judge_state.player_id == g.player.id, \
           "You're not the judge this round."
    assert g.player.id != content["username"]
    assert all_cards_down(match)
    assert all([not state.round_winner for state in match.states])

    winner_state = get_state(content["username"], match.id)
    winner_state.round_winner = True
    winner_state.score += 1

    if winner_state.score == match.max_score:
        match.winner_id = winner_state.id
        match.status = "ENDED"
        db.session.add(match)

    db.session.add(judge_state)
    db.session.add(winner_state)
    db.session.commit()

    if match.status == "ENDED":
        return jsonify(status="success",
                       match_status="ENDED",
                       winner=Player.query.get(match.winner_id).username)

    if content["ignore_ack"]:
        return new_round(match)
    return jsonify(status="success")


@jsonify_assertion_error
@app.route("/matches/<int:match_id>/acknowledge", methods=["POST"])
@auth.login_required
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

    assert g.player.id in [state.player_id for state in match.states], \
           "You're not in this game!"
    assert all_cards_down(match), "Not all players have put down cards."
    assert any([state.round_winner for state in match.states]), \
           "A winner has not been chosen yet."

    state = get_state(g.player.id, match.id)
    state.viewed_round_end = True

    db.session.add(state)
    db.session.commit()

    if all_viewed_round_end(match):
        return new_round(match)
    return jsonify(status="success")
