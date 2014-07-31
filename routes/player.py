from routes.shared import *
from sqlalchemy.exc import IntegrityError


def get_friends():
    """This method is very expensive and bad."""
    friendships = FriendshipManager.query.filter_by(requester=g.player.id,
                                                    accepted=True).all()
    friendships += FriendshipManager.query.filter_by(requestee=g.player.id,
                                                     accepted=True).all()
    friends = [friendship.requester for friendship in friendships
               if friendship.requester != g.player.id]
    friends += [friendship.requestee for friendship in friendships
                if friendship.requestee != g.player.id]
    friends = [Player.query.get_or_404(player_id) for player_id in friends]
    return [{"username": friend.username,
             "first_name": friend.first_name,
             "last_name": friend.last_name}
            for friend in friends]


def get_friend_requests():
    """
    This method returns all players that have sent
    player_id an invite. It is very expensive and bad.
    """

    friendships = FriendshipManager.query.filter_by(requestee=g.player.id,
                                                    accepted=False).all()
    friend_requesters = [Player.query.get_or_404(friendship.requester)
                         for friendship in friendships]
    return [{"username": requester.username,
             "first_name": requester.first_name,
             "last_name": requester.last_name}
            for requester in friend_requesters]


def get_pending_friends():
    """
    This method returns all players that player_id
    has sent an invite to. It is very expensive and bad.
    """

    friendships = FriendshipManager.query.filter_by(requester=g.player.id,
                                                    accepted=False).all()
    friend_requestees = [Player.query.get_or_404(friendship.requestee)
                         for friendship in friendships]
    return [{"username": requestee.username,
             "first_name": requestee.first_name,
             "last_name": requestee.last_name}
            for requestee in friend_requestees]


def get_friends_list():
    """Returns sum of get_friends, friend_requests, pending_friends."""
    return {"pending_friends": get_pending_friends(),
            "friend_requests": get_friend_requests(),
            "friends": get_friends()}


@jsonify_assertion_error
@app.route("/players", methods=["GET"])
@auth.login_required
def get_all_players():
    players = Player.query.all()
    players = [{"username": player.username,
                "first_name": player.first_name,
                "last_name": player.last_name,
                "email": player.email}
               for player in players]
    return jsonify(status="success", players=players)


@jsonify_assertion_error
@app.route("/players/login", methods=["GET"])
@auth.login_required
def login_player():
    return jsonify(status="success",
                   username=g.player.username,
                   email=g.player.email,
                   token=g.player.generate_auth_token(),
                   first_name=g.player.first_name,
                   last_name=g.player.last_name)


@jsonify_assertion_error
@app.route("/player", methods=["GET"])
@auth.login_required
def get_player_info():
    wins = len(Match.query.filter_by(winner_id=g.player.id).all())
    hosting = Match.query.filter_by(host_id=g.player.id).all()

    # There has got to be a better way to do all of this
    states = State.query.filter_by(player_id=g.player.id).all()
    matches = []
    for state in states:
        match = get_match(state.match_id)
        matches.append(match)
    matches = [match for match in matches if match not in hosting]
    return jsonify(status="success",
                   username=g.player.username,
                   email=g.player.email,
                   first_name=g.player.first_name,
                   last_name=g.player.last_name,
                   wins=wins,
                   matches=[{"id": match.id,
                             "name": match.name,
                             "status": match.status}
                            for match in matches],
                   hosting=[{"id": match.id,
                             "name": match.name,
                             "status": match.status}
                            for match in hosting],
                   invites=[{"id": match.id, "name": match.name}
                            for match in g.player.invited])


@jsonify_assertion_error
@app.route("/players", methods=["DELETE"])
@auth.login_required
def delete_player():
    """Debug purposes only."""
    db.session.delete(g.player)
    db.session.commit()
    return jsonify(status="success")


@jsonify_assertion_error
@app.route("/players", methods=["POST"])
def create_player():
    content = request.json
    player = Player(content["username"],
                    content["password"],
                    content["email"],
                    content["first_name"],
                    content["last_name"])
    db.session.add(player)
    try:
        db.session.commit()
    except IntegrityError:
        return jsonify(status="failure", message="Username or email in use.")
    return jsonify(status="success", token=player.generate_auth_token())


@jsonify_assertion_error
@app.route("/players/befriend", methods=["POST"])
@auth.login_required
def send_friend_request():
    content = request.json
    requestee = get_player(content["username"])
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


@jsonify_assertion_error
@app.route("/players/accept", methods=["POST"])
@auth.login_required
def accept_friend_request():
    content = request.json
    requester = get_player(content["username"])
    friendship = FriendshipManager.query.filter_by(requester=requester.id,
                                                   requestee=g.player.id,
                                                   accepted=False).first()
    friendship.accepted = True
    db.session.add(friendship)
    db.session.commit()
    return jsonify(status="success")


@jsonify_assertion_error
@app.route("/players/reject", methods=["POST"])
@auth.login_required
def reject_friend_request():
    content = request.json
    requester = get_player(content["username"])
    friendship = FriendshipManager.query.filter_by(requester=requester.id,
                                                   requstee=g.player.id,
                                                   accepted=False).first()
    db.session.remove(friendship)
    db.session.commit()
    return jsonify(status="success")


@jsonify_assertion_error
@app.route("/players/friends", methods=["GET"])
@auth.login_required
def get_friends_route():
    return jsonify(status="success", friends=get_friends())


@jsonify_assertion_error
@app.route("/players/friend_requests", methods=["GET"])
@auth.login_required
def get_friend_requests_route():
    return jsonify(status="success",
                   friend_requests=get_friend_requests())


@jsonify_assertion_error
@app.route("/players/pending_friends", methods=["GET"])
@auth.login_required
def get_pending_friends_route():
    return jsonify(status="success",
                   pending_friends=get_pending_friends())


@jsonify_assertion_error
@app.route("/players/friends_list", methods=["GET"])
@auth.login_required
def get_friends_list_route():
    return jsonify(status="success", **get_friends_list())


@jsonify_assertion_error
@app.route("/players/search", methods=["POST"])
@auth.login_required
def search_players():
    content = request.json
    query = content["query"]
    players = Player.query.filter(
                    Player.first_name.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.username.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.last_name.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.email.ilike("%{}%".format(query))).all()

    players = [{"id": player.id,
                "username": player.username,
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
                      player["id"] != g.player.id]
    return jsonify(status="success",
                   players=players)
