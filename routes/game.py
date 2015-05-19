"""
    routes.game
    ~~~~~
    Endpoints and controller
    logic for gameplay.
"""

from routes.shared import *


@app.route('/game/create', methods=['POST'])
@with_user
@with_content
def create(user, content):
    name        = content['name']
    max_points  = content['max_points']
    max_players = content['max_players']
    emails      = content['emails']

    game = Game.create(
        user, name, max_points, max_players
    )
    users   = User.get_all(emails) + [user]
    players = Player.create_all(users, game)
    game.invite_all(players)

    return jsonify(**{
        'id'         : game.id,
        'name'       : game.name,
        'max_points' : game.max_points,
        'max_players': game.max_players,
        'players'    : [
            {
                'name'  : player.user.name,
                'email' : player.user.email,
                'status': player.status
            }
            for player in game.players
        ],
        'status'     : game.status
    })


@app.route('/game/<int:id>/invite', methods=['POST'])
@with_user
@with_content
def invite(id, user, content):
    email = content['email']
    other = User.get(email)
    game  = Game.get(id)

    assert user == game.host
    assert game.status == 'PENDING'

    player = Player.create(other, game)
    game.invite(player)

    return jsonify()


@app.route('/game/<int:id>', methods=['POST'])
@with_user
@with_content
def get(id, user, content):
    game   = Game.get(id)
    player = Player.get(user, game)
    assert player in game.players

    if game.status == 'PENDING':
        return jsonify(**{
            'id'         : game.id,
            'name'       : game.name,
            'max_points' : game.max_points,
            'max_players': game.max_players,
            'status'     : game.status,
            'players'    : [
                {
                    'name'  : player.user.name,
                    'email' : player.user.email,
                    'status': player.status
                }
                for player in game.players
            ]
        })

    elif game.status == 'ONGOING':
        return jsonify(**{
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
                'name' : game.judge.user.name,
                'email': game.judge.user.email,
            },
            'players'    : [
                {
                    'name'  : player.user.name,
                    'email' : player.user.email,
                    'status': player.status
                }
                for player in game.players
            ],
            'previous'   : game.previous_round
        })

    # TODO
    # elif game.status == 'ENDED':

    return jsonify(), 404


@app.route('/game/<int:id>/<action>', methods=['POST'])
@with_user
@with_content
def accept_or_decline(id, action, user, content):
    player  = Player.get(user, game)
    started = False

    if action == 'add':
        player.set_status_joined()
        joined = [player for player in game.players
                         if player.status == 'JOINED']
        game = Game.get(id)

        if len(joined) == game.max_players:
            game.start()
            started = True

    elif action == 'delete':
        player.delete()

    else:
        return jsonify(), 404

    return jsonify(started=started)


@app.route('/game/<int:id>/play', methods=['POST'])
@with_user
@with_content
def play(id, user, content):
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

    return jsonify()
