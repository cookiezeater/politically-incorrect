"""
    routes.game
    ~~~~~
    Endpoints and controller
    logic for main gameplay.
"""

from routes.shared import *


@app.route('/game/create', methods=['POST'])
@with_user
def create(user, content):
    name        = content['name']
    max_points  = content['max_points']
    max_players = content['max_players']
    emails      = content['emails']
    status      = 'PENDING'

    game = Game.create(
        user, name, max_points, max_players, status
    )

    users   = User.get_all(emails)  # User.query.filter(or_(User.email == email for email in players)) + [user]
    players = Player.create_all(users, game)
    game.invite_all(players)

    result = {
        'id'         : game.id,
        'name'       : game.name,
        'max_points' : game.max_points,
        'max_players': game.max_players,
        'players'    : [
            {
                'name'  : player.user.name,
                'email' : player.email.name,
                'status': player.status
            }
            for player in game.players
        ],
        'status'     : game.status
    }
    return jsonify(**result), 200


@app.route('/game/<int:id>/invite', methods=['POST'])
@with_user
def invite(user, content, id):
    email   = content['email']
    other   = User.get(email)
    game    = Game.get(id)

    assert user == game.host
    assert game.status == 'PENDING'

    player = Player.create(other, game)
    game.invite(player)

    return jsonify(), 200


@app.route('/game/<int:id>', methods=['POST'])
@with_user
def get(user, content, id):
    game   = Game.get(id)
    player = Player.get(user, game)
    assert player in game.players

    if game.status == 'PENDING':
        result = {
            'id'         : game.id,
            'name'       : game.name,
            'max_points' : game.max_points,
            'max_players': game.max_players,
            'status'     : game.status,
            'players'    : [
                {
                    'name'  : player.user.name,
                    'email' : player.email.name,
                    'status': player.status
                }
                for player in game.players
            ]
        }

    elif game.status == 'ONGOING':
        result = {
            'id'         : game.id,
            'name'       : game.name,
            'max_points' : game.max_points,
            'max_players': game.max_players,
            'status'     : game.status,
            'black_card' : {
                'text'   : game.black_card.text,
                'answers': game.black_card.answers
            },
            'table'      : [
                {
                    'email': player.user.email,
                    'id'   : card.id,
                    'text' : card.text
                }
                for player.card in game.players if player.card
            ],
            'hand'       : [
                {
                    'id'  : card.id,
                    'text': card.text
                }
                for card in player.hand
            ],
            'judge'      : {
                'name' : game.judge.name,
                'email': game.judge.email,
            },
            'players'    : [
                {
                    'name'  : player.user.name,
                    'email' : player.email.name,
                    'status': player.status
                }
                for player in game.players
            ],
            'previous'   : game.previous_round
        }

    # TODO
    # elif game.status == 'ENDED':
    else:
        return jsonify(), 404

    return jsonify(**result), 200


@app.route('/game/<action>', methods=['POST'])
@with_user
def accept_or_decline(user, content, action):
    game    = content['id']
    player  = Player.get(user, game)
    result  = { 'started': False }

    if action == 'add':
        player.set_status_joined()
        joined = [player for player in Player.get_all(game)
                         if player.status == 'JOINED']
        game = Game.get(game)

        if len(joined) == game.max_players:
            game.start()
            result['started'] = True

    elif action == 'delete':
        player.delete()

    else:
        return jsonify(), 404

    return jsonify(**result), 200


@app.route('/game/<int:id>/play', methods=['POST'])
@with_user
def play(user, content, id):
    """
    Handle main gameplay. If the requesting user
    is the current judge, then expect an email
    in the request body and interpret it as
    the round winner chosen by the judge. Otherwise,
    the request body should contain a card id in the
    user's hand, which should be placed on the table.

    request :=
        POST ({
            'card_id': int
        } | {
            'email': str
        })
    """

    game = Game.get(id)

    if user == game.judge.user:
        email  = content['email']
        winner = next(
            (player for player in game.players if player.user.email == email),
            None
        )
        winner.add_points(1)
        game.new_round()

    else:
        player = Player.get(user, game)

        if not player.card:
            return jsonify(), 418

        card_id = content['card_id']
        card    = next(
            (card for card in player.hand if card.id == card_id),
            None
        )
        player.play_card(card)
        player.draw()

    return jsonify(), 200
