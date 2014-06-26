from routes.shared import *


@app.route("/players", methods=["GET"])
def get_all_players():
    players = Player.query.all()
    players = {player.email: player.id
               for player in players}
    return jsonify(**players)

@app.route("/players/<int:player_id>", methods=["GET"])
def get_player(player_id):
    player = Player.query.get(player_id)
    return jsonify(username=player.username,
                   email=player.email,
                   first_name=player.first_name,
                   last_name=player.last_name,
                   invited=[invitation.id for invitation in player.invited])

@app.route("/players/<int:player_id>", methods=["PUT"])
def update_player(player_id):
    player = Player.query.get(player_id)
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

    player = Card.query.get(player_id)
    db.session.delete(player)
    db.session.commit()
    return jsonify(status="success")

@app.route("/players", methods=["POST"])
def create_player():
    content = request.json
    prev_player = Player.query.filter(Player.email == content["email"])
    if prev_player:
        return jsonify(status="Email is associated with another player.")
    player = Player(content["username"],
                    content["password"],
                    content["email"],
                    content["first_name"],
                    content["last_name"])
    db.session.add(player)
    db.session.commit()
    return jsonify(status="success")