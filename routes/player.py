from routes.shared import *
from sqlalchemy.exc import IntegrityError


@app.route("/players", methods=["GET"])
def get_all_players():
    players = Player.query.all()
    players = {player.email: player.id for player in players}
    return jsonify(**players)


@app.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = Player.query.get_or_404(player_id)
    return jsonify(username=player.username,
                   email=player.email,
                   first_name=player.first_name,
                   last_name=player.last_name)


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
    assert FriendshipManager.query.filter_by(requester=requestee_id,
                                             requestee=requester_id).first() \
                                            is None
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

@app.route("/players/<int:player_id>/friends", methods=["POST"])
def get_friends(player_id):
    # Eventually, request.json must contain some verification token
    # and merge queries somehow
    content = request.json
    friendships = FriendshipManager.query.filter_by(requester=player_id,
                                                    accepted=True)
    friendships += FriendshipManager.query.filter_by(requestee=player_id,
                                                     accepted=True)
    friends = [friendship.requester for friendship in friendships
               if friendship.requester != player_id]
    friends += [friendship.requestee for friendship in friendships
                if friendship.requestee != player_id]
    return jsonify(status="success", friends=friends)
