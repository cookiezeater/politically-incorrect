from routes.shared import *


@app.route("/users", methods=["GET"])
def get_all_users():
    players = Player.query.all()
    players = {player.email: player.id
               for player in players}
    return jsonify(**players)


@app.route("/users/<int:player_id>", methods=["GET"])
def get_user(player_id):
    player = Player.query.get(player_id)
    return jsonify(username=player.username,
                   email=player.email,
                   first_name=player.first_name,
                   last_name=player.last_name)


@app.route("/users/<int:player_id>", methods=["PUT"])
def get_user(player_id):
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


@app.route("/users", methods=["POST"])
def create_user():
    content = request.json
    player = Player(content["username"],
                    content["password"],
                    content["email"],
                    content["first_name"],
                    content["last_name"])
    db.session.add(player)
    db.session.commit()
    return jsonify(status="success")
