from routes.shared import *
from sqlalchemy.exc import IntegrityError


@app.route("/players", methods=["GET"])
def get_all_players():
    players = Player.query.all()
    players = {player.email: player.id for player in players}
    return jsonify(status="success", **players)


@jsonify_assertion_error
@app.route("/players/login", methods=["POST"])
def login_player():
    content = request.json
    try:
        player = Player.query.filter_by(username=content["username"],
                                        password=content["password"]).first()
    except:
        return jsonify(status="failure", message="Invalid username or password")
    return jsonify(status="success",
                   username=player.username,
                   password=player.password,
                   player_id=player.id,
                   first_name=player.first_name,
                   last_name=player.last_name,
                   email=player.email)


@app.route("/players/<int:player_id>", methods=["POST"])
def get_player_info(player_id):
    content = request.json
    player = get_player(player_id, content["password"])

    wins = len(Match.query.filter_by(winner_id=player_id).all())
    hosting = Match.query.filter_by(host_id=player_id).all()

    # There has got to be a better way to do all of this
    states = State.query.filter_by(player_id=player_id).all()
    matches = []
    for state in states:
        match = get_match(state.match_id)
        matches.append(match)
    matches = [match for match in matches if match not in hosting]

    return jsonify(status="success",
                   username=player.username,
                   email=player.email,
                   first_name=player.first_name,
                   last_name=player.last_name,
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
                            for match in player.invited])


@app.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    """Debug purposes only."""
    player = Card.query.get_or_404(player_id)
    db.session.delete(player)
    db.session.commit()
    return jsonify(status="success")


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
    return jsonify(status="success", player_id=player.id)


@app.route("/players/<int:player_id>/befriend", methods=["POST"])
def send_friend_request(player_id):
    content = request.json
    requester = get_player(content["player_id"], content["password"])
    requestee = get_player(player_id)
    assert requestee.id != requester.id
    assert FriendshipManager.query.filter_by(requestee=requestee.id,
                                             requester=requester.id).first() \
                                            is None
    assert FriendshipManager.query.filter_by(requester=requestee.id,
                                             requestee=requester.id).first() \
                                            is None
    friendship = FriendshipManager(requester.id, requestee.id)
    db.session.add(friendship)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/<int:player_id>/accept", methods=["POST"])
def accept_friend_request(player_id):
    content = request.json
    requester = get_player(player_id)
    requestee = get_player(content["player_id"], content["password"])
    friendship = FriendshipManager.query.filter_by(requester=requester.id,
                                                   requestee=requestee.id,
                                                   accepted=False).first()
    friendship.accepted = True
    db.session.add(friendship)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/<int:player_id>/reject", methods=["POST"])
def reject_friend_request(player_id):
    content = request.json
    requester = get_player(player_id)
    rejector = get_player(content["player_id"], content["password"])
    friendship = FriendshipManager.query.filter_by(requester=requester.id,
                                                   requstee=requestee.id,
                                                   accepted=False).first()
    db.session.remove(friendship)
    db.session.commit()
    return jsonify(status="success")


def get_friends(player_id):
    """This method is very expensive and bad."""
    content = request.json
    password = Player.query.get_or_404(player_id).password
    assert request.json["password"] == password
    friendships = FriendshipManager.query.filter_by(requester=player_id,
                                                    accepted=True).all()
    friendships += FriendshipManager.query.filter_by(requestee=player_id,
                                                     accepted=True).all()
    friends = [friendship.requester for friendship in friendships
               if friendship.requester != player_id]
    friends += [friendship.requestee for friendship in friendships
                if friendship.requestee != player_id]
    friends = [Player.query.get_or_404(player_id) for player_id in friends]
    return [{"id": friend.id,
             "username": friend.username,
             "first_name": friend.first_name,
             "last_name": friend.last_name}
            for friend in friends]


@app.route("/players/<int:player_id>/friends", methods=["POST"])
def get_friends_route(player_id):
    return jsonify(status="success", friends=get_friends(player_id))


def get_friend_requests(player_id):
    """
    This method returns all players that have sent
    player_id an invite. It is very expensive and bad.
    """

    content = request.json
    player = get_player(player_id, content["password"])
    friendships = FriendshipManager.query.filter_by(requestee=player.id,
                                                    accepted=False).all()
    friend_requesters = [Player.query.get_or_404(friendship.requester)
                         for friendship in friendships]
    return [{"id": requester.id,
             "username": requester.username,
             "first_name": requester.first_name,
             "last_name": requester.last_name}
            for requester in friend_requesters]


@app.route("/players/<int:player_id>/friend_requests", methods=["POST"])
def get_friend_requests_route(player_id):
    return jsonify(status="success",
                   friend_requests=get_friend_requests(player_id))


def get_pending_friends(player_id):
    """
    This method returns all players that player_id
    has sent an invite to. It is very expensive and bad.
    """

    content = request.json
    player = get_player(player_id, content["password"])
    friendships = FriendshipManager.query.filter_by(requester=player.id,
                                                    accepted=False).all()
    friend_requestees = [Player.query.get_or_404(friendship.requestee)
                         for friendship in friendships]
    return [{"id": requestee.id,
             "username": requestee.username,
             "first_name": requestee.first_name,
             "last_name": requestee.last_name}
            for requestee in friend_requestees]


@app.route("/players/<int:player_id>/pending_friends", methods=["POST"])
def get_pending_friends_route(player_id):
    return jsonify(status="success",
                   pending_friends=get_pending_friends(player_id))


def get_friends_list(player_id):
    """Returns sum of get_fruends, friend_requests, pending_friends."""
    content = request.json
    player = get_player(player_id, content["password"])
    return {"pending_friends": get_pending_friends(player.id),
            "friend_requests": get_friend_requests(player.id),
            "friends": get_friends(player.id)}


@app.route("/players/<int:player_id>/friends_list", methods=["POST"])
def get_friends_list_route(player_id):
    return jsonify(status="success", **get_friends_list(player_id))


@app.route("/players/search/<string:query>", methods=["POST"])
def search_players(query):
    content = request.json
    player = get_player(content["player_id"])
    players = Player.query.filter(
                    Player.first_name.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.username.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.last_name.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.email.ilike("%{}%".format(query))).all()

    players = [{"id": person.id,
                "username": person.username,
                "first_name": person.first_name,
                "last_name": person.last_name}
               for person in players]
    # Prune duplicates
    players = [dict(person) for person in
                            set([tuple(person.items()) for person in players])]
    friends_list = get_friends_list(player.id)
    friends_list_flattened = [person for player_list in friends_list
                                     for person in friends_list[player_list]]
    players = [person for person in players
                      if person not in friends_list_flattened and
                      person["id"] != player.id]
    return jsonify(status="success",
                   players=players)
