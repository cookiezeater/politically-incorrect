from routes.shared import *
from sqlalchemy.exc import IntegrityError


@app.route("/players", methods=["GET"])
def get_all_players():
    players = Player.query.all()
    players = {player.email: player.id for player in players}
    return jsonify(**players)


@app.route("/players/login", methods=["POST"])
def login_player():
    content = request.json
    player = Player.query.filter_by(username=content["username"],
                                    password=content["password"]) \
                                   .first()
    return jsonify(player_id=player.id)


@app.route("/players/<int:player_id>", methods=["POST"])
def get_player_info(player_id):
    content = request.json
    player = Player.query.get(player_id)
    assert player.password == content["password"]
    wins = len(Match.query.filter_by(winner_id=player_id).all())
    hosting = len(Match.query.filter_by(host_id=player_id).all())
    return jsonify(wins=wins, hosting=hosting)


@app.route("/players/<int:player_id>", methods=["PUT"])
def update_player(player_id):
    player = Player.query.get_or_404(player_id)
    content = request.json
    if "username" in content:
        player.username = content[username]
    if "password" in content:
        player.password = content[password]
    if "email" in content:
        player.email = content[email]
    if "first_name" in content:
        player.first_name = content[first_name]
    if "last_name" in content:
        player.last_name = content[last_name]
    db.session.add(player)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/<int:player_id>", methods=["DELETE"])
def delete_player(player_id):
    """Deleting a player cascades to all of its relationships."""
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
        return jsonify(status="failure", message="Username or email in-use.")
    return jsonify(status="success", player_id=player.id)


@app.route("/players/<int:player_id>/befriend", methods=["POST"])
def send_friend_request(player_id):
    content = request.json
    requester_id = content["player_id"]
    requestee_id = player_id
    assert requestee_id != requester_id
    assert FriendshipManager.query.filter_by(requestee=requestee_id,
                                             requester=requester_id).first() \
                                            is None
    assert FriendshipManager.query.filter_by(requester=requestee_id,
                                             requestee=requester_id).first() \
                                            is None
    player = Player.query.get(requester_id)
    assert player is not None
    assert player.password == content["password"]
    assert Player.query.get(requestee_id) is not None
    friendship = FriendshipManager(requester_id, requestee_id)
    db.session.add(friendship)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/<int:player_id>/accept", methods=["POST"])
def accept_friend_request(player_id):
    content = request.json
    requester_id = player_id
    requestee_id = content["player_id"]
    friendship = FriendshipManager.query.filter_by(requester=requester_id,
                                                   requestee=requestee_id,
                                                   accepted=False).first()
    friendship.accepted = True
    db.session.add(friendship)
    db.session.commit()
    return jsonify(status="success")


@app.route("/players/<int:player_id>/reject", methods=["POST"])
def reject_friend_request(player_id):
    content = request.json
    requester = Player.query.get(player_id)
    rejector = Player.query.get(content["player_id"])
    friendship = FriendshipManager.query.filter_by(requester=requester_id,
                                                   requstee=requestee_id,
                                                   accepted=False).first()
    db.session.remove(friendship)
    db.session.commit()
    return jsonify(status="success")


def get_friends(player_id):
    """This method is very expensive and bad."""
    content = request.json
    assert request.json["password"] == Player.query.get(player_id).password
    friendships = FriendshipManager.query.filter_by(requester=player_id,
                                                    accepted=True).all()
    friendships += FriendshipManager.query.filter_by(requestee=player_id,
                                                     accepted=True).all()
    friends = [friendship.requester for friendship in friendships
               if friendship.requester != player_id]
    friends += [friendship.requestee for friendship in friendships
                if friendship.requestee != player_id]
    friends = [Player.query.get(player_id) for player_id in friends]
    return {str(friend.id):
            {"username": friend.username,
             "first_name": friend.first_name,
             "last_name": friend.last_name}
            for friend in friends}


@app.route("/players/<int:player_id>/friends", methods=["POST"])
def get_friends_route(player_id):
    return jsonify(status="success", **get_friends(player_id))


def get_friend_requests(player_id):
    """
    This method returns all players that have sent
    player_id an invite. It is very expensive and bad.
    """

    content = request.json
    assert request.json["password"] == Player.query.get(player_id).password
    friendships = FriendshipManager.query.filter_by(requestee=player_id,
                                                    accepted=False).all()
    friend_requesters = [Player.query.get(friendship.requester)
                         for friendship in friendships]
    return {str(requester.id):
            {"username": requester.username,
             "first_name": requester.first_name,
             "last_name": requester.last_name}
            for requester in friend_requesters}


@app.route("/players/<int:player_id>/friend_requests", methods=["POST"])
def get_friend_requests_route(player_id):
    return jsonify(status="success", **get_friend_requests(player_id))


def get_pending_friends(player_id):
    """
    This method returns all players that player_id
    has sent an invite to. It is very expensive and bad.
    """

    content = request.json
    assert request.json["password"] == Player.query.get(player_id).password
    friendships = FriendshipManager.query.filter_by(requester=player_id,
                                                    accepted=False).all()
    friend_requestees = [Player.query.get(friendship.requestee)
                         for friendship in friendships]
    return {str(requestee.id):
            {"username": requestee.username,
             "first_name": requestee.first_name,
             "last_name": requestee.last_name}
            for requestee in friend_requestees}


@app.route("/players/<int:player_id>/pending_friends", methods=["POST"])
def get_pending_friends_route(player_id):
    return jsonify(status="success", **get_pending_friends(player_id))


def get_friends_list(player_id):
    """Returns sum of get_fruends, friend_requests, pending_friends."""
    content = request.json
    assert request.json["password"] == Player.query.get(player_id).password
    return {"pending_friends": get_pending_friends(player_id),
            "friend_requests": get_friend_requests(player_id),
            "friends": get_friends(player_id)}


@app.route("/players/<int:player_id>/friends_list", methods=["POST"])
def get_friends_list_route(player_id):
    return jsonify(status="success", **get_friends_list(player_id))


@app.route("/players/search/<string:query>", methods=["POST"])
def search_players(query):
    content = request.json
    player = Player.query.get(content["player_id"])
    assert player is not None
    assert content["password"] == player.password
    players = Player.query.filter(
                    Player.first_name.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.username.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.last_name.ilike("%{}%".format(query))).all()
    players += Player.query.filter(
                    Player.email.ilike("%{}%".format(query))).all()
    friends_list = get_friends_list(player.id)
    players = set([person for person in players
                   if str(person.id) not in friends_list["pending_friends"]
                   and str(person.id) not in friends_list["friend_requests"]
                   and str(person.id) not in friends_list["friends"]
                   and person.id != player.id])
    return jsonify(status="success",
                   **{str(player.id):
                      {"username": player.username,
                       "first_name": player.first_name,
                       "last_name": player.last_name}
                      for player in players})
