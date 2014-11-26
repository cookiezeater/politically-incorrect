import requests
from routes.shared import *
from sqlalchemy.exc import IntegrityError

GOOGLE_URL = "https://www.googleapis.com/oauth2/v1/userinfo?access_token={}"


def get_friends(player):
    """This method is very expensive and bad."""
    friendships = FriendshipManager.query.filter_by(requester=player.id,
                                                    accepted=True).all()
    friendships += FriendshipManager.query.filter_by(requestee=player.id,
                                                     accepted=True).all()
    friends = [friendship.requester for friendship in friendships
               if friendship.requester != player.id]
    friends += [friendship.requestee for friendship in friendships
                if friendship.requestee != player.id]
    friends = [Player.query.get_or_404(player_id) for player_id in friends]
    return [{"email": friend.email,
             "first_name": friend.first_name,
             "last_name": friend.last_name}
            for friend in friends]


def get_friend_requests(player):
    """
    This method returns all players that have sent
    player_id an invite. It is very expensive and bad.
    """

    friendships = FriendshipManager.query.filter_by(requestee=player.id,
                                                    accepted=False).all()
    friend_requesters = [Player.query.get_or_404(friendship.requester)
                         for friendship in friendships]
    return [{"email": requester.email,
             "first_name": requester.first_name,
             "last_name": requester.last_name}
            for requester in friend_requesters]


def get_pending_friends(player):
    """
    This method returns all players that player_id
    has sent an invite to. It is very expensive and bad.
    """

    friendships = FriendshipManager.query.filter_by(requester=player.id,
                                                    accepted=False).all()
    friend_requestees = [Player.query.get_or_404(friendship.requestee)
                         for friendship in friendships]
    return [{"email": requestee.email,
             "first_name": requestee.first_name,
             "last_name": requestee.last_name}
            for requestee in friend_requestees]


def get_friends_list(player):
    """Returns sum of get_friends, friend_requests, pending_friends."""
    return {"pending_friends": get_pending_friends(player),
            "friend_requests": get_friend_requests(player),
            "friends": get_friends(player)}


def login(content, player):
    token = content["token"]
    response = requests.get(GOOGLE_URL.format(token)).json()
    assert "error" not in response, "Invalid Google account."
    player.phone_id = content["phone_id"]
    db.session.commit()
    return get_player_info(player, player.generate_auth_token())


def register(content):
    token = content["token"]
    response = requests.get(GOOGLE_URL.format(token)).json()
    assert "error" not in response, "Invalid Google account."
    player = Player("google",
                    content["email"],
                    None,
                    response["given_name"],
                    response["family_name"],
                    content["phone_id"])
    db.session.add(player)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(status="failure",
                       message="Username or email in use.")
    return get_player_info(player, player.generate_auth_token())


def get_player_info(player, token=""):
    wins = len(Match.query.filter_by(winner_id=player.id).all())
    hosting = Match.query.filter_by(host_id=player.id).all()

    # There has got to be a better way to do all of this
    states = State.query.filter_by(player_id=player.id).all()
    matches = []
    for state in states:
        matches.append(state.match)
    matches = [match for match in matches]
    return jsonify(status="success",
                   email=player.email,
                   token=token,
                   first_name=player.first_name,
                   last_name=player.last_name,
                   wins=wins,
                   pending_friends=get_pending_friends(player),
                   friend_requests=get_friend_requests(player),
                   friends=get_friends(player),
                   ongoing=get_match_beans(matches, key=lambda match: match.status == "ONGOING"),
                   pending=get_match_beans(matches, key=lambda match: match.status == "PENDING"),
                   invites=get_match_beans(player.invited))


def get_match_beans(matches, key=lambda match: True):
    return [{"id": match.id,
             "name": match.name,
             "status": match.status,
             "player_first_names": [state.player.first_name for state in match.states]}
            for match in matches if key(match)]


@app.route("/players", methods=["DELETE"])
@jsonify_assertion_error
@admin_required
@auth.login_required
def delete_player():
    """Debug purposes only."""
    db.session.delete(g.player)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players", methods=["POST"])
@jsonify_assertion_error
def enter_player():
    content = request.json
    assert "player_type" in content, "Invalid request."
    exists = Player.query.filter_by(email=content["email"]).first()
    if exists:
        return login(content, exists)
    else:
        return register(content)


@app.route("/players/info", methods=["POST"])
@jsonify_assertion_error
@auth.login_required
def get_info():
    content = request.json
    g.player.phone_id = content["phone_id"]
    db.session.commit()
    return get_player_info(g.player)


@app.route("/players/befriend", methods=["POST"])
@jsonify_assertion_error
@auth.login_required
def send_friend_request():
    content = request.json
    requestee = get_player(content["email"])
    assert requestee.id != g.player.id
    assert FriendshipManager.query.filter_by(requestee=requestee.id,
                                             requester=g.player.id).first() \
                                            is None
    assert FriendshipManager.query.filter_by(requester=requestee.id,
                                             requestee=g.player.id).first() \
                                            is None
    friendship = FriendshipManager(g.player.id, requestee.id)
    db.session.add(friendship)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/accept", methods=["POST"])
@jsonify_assertion_error
@auth.login_required
def accept_friend_request():
    content = request.json
    requester = get_player(content["email"])
    friendship = FriendshipManager.query.filter_by(requester=requester.id,
                                                   requestee=g.player.id,
                                                   accepted=False).first()
    friendship.accepted = True
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/reject", methods=["POST"])
@jsonify_assertion_error
@auth.login_required
def reject_friend_request():
    content = request.json
    requester = get_player(content["email"])
    friendship = FriendshipManager.query.filter_by(requester=requester.id,
                                                   requstee=g.player.id,
                                                   accepted=False).first()
    db.session.remove(friendship)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/friends", methods=["GET"])
@jsonify_assertion_error
@auth.login_required
def get_friends_route():
    return jsonify(status="success", friends=get_friends())


@app.route("/players/friend_requests", methods=["GET"])
@jsonify_assertion_error
@auth.login_required
def get_friend_requests_route():
    return jsonify(status="success",
                   friend_requests=get_friend_requests())


@app.route("/players/pending_friends", methods=["GET"])
@jsonify_assertion_error
@auth.login_required
def get_pending_friends_route():
    return jsonify(status="success",
                   pending_friends=get_pending_friends())


@app.route("/players/friends_list", methods=["GET"])
@jsonify_assertion_error
@auth.login_required
def get_friends_list_route():
    return jsonify(status="success", **get_friends_list())


@app.route("/players/search", methods=["POST"])
@jsonify_assertion_error
@auth.login_required
def search_players():
    content = request.json
    query = content["query"]
    players = Player.query.filter(
                    Player.first_name.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.email.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.last_name.ilike("%{}%".format(query))).all()

    players = [{"email": player.email,
                "first_name": player.first_name,
                "last_name": player.last_name}
               for player in players]

    # Prune duplicates
    players = [dict(player) for player in
                            set([tuple(player.items()) for player in players])]
    friends_list = get_friends_list()
    friends_list_flattened = [player for player_list in friends_list
                                     for player in friends_list[player_list]]

    players = [player for player in players
                      if player not in friends_list_flattened and
                      player["email"] != g.player.email]
    return jsonify(status="success",
                   players=players)


@app.route("/players/befriend/start")
@jsonify_assertion_error
@auth.login_required
def add_all_email_friends():
    content = request.json
    emails = content["emails"]
    players = Player.query.filter(Player.email.in_(friends)).all()
    # for player in players:
