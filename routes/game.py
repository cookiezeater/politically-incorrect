"""
    routes.game
    ~~~~~
    Endpoints and controller
    logic for gameplay.
"""

from flask import jsonify

from common import app, db
from util import with_content, with_user
from models import (
    Game,
    Player,
    User
)


@app.route('/game/create', methods=['POST'])
@with_user
@with_content
def create_game(user, content):
    """Creates a pending game."""
    name        = content['name']
    max_points  = content['max_points']
    max_players = content['max_players']
    random      = content['random']
    emails      = content['emails']

    game = Game.create(
        user, name, max_points, max_players, random
    )
    users   = User.get_all(emails) + [user]
    players = Player.create_all(users, game)
    game.invite_all(players)

    player = next(
        (player for player in players if player.user == user),
        None
    )
    player.set_status_joined()

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

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


@app.route('/game/<int:id>/invite', methods=['POST'])
@with_user
@with_content
def invite(id, user, content):
    """Invites a list of users."""
    game = Game.get(id)
    assert user == game.host
    assert game.status == Game.PENDING

    emails  = content['emails']
    users   = User.get_all(emails)
    players = Player.create_all(users, game)
    game.invite_all(players)

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return jsonify()


@app.route('/game/<int:id>', methods=['POST'])
@with_user
@with_content
def get_game(id, user, content):
    game   = Game.get(id)
    player = Player.get(user, game)
    assert player in [p for p in game.players if p.status != Player.REJECTED]

    if game.status == Game.PENDING:
        return jsonify(**{
            'id'         : game.id,
            'host'       : {
                'name' : game.host.name,
                'email': game.host.email
            },
            'name'       : game.name,
            'max_points' : game.max_points,
            'max_players': game.max_players,
            'status'     : game.status,
            'players'    : [
                {
                    'name'  : player.user.name,
                    'email' : player.user.email,
                    'status': player.status,
                    'points': 0
                }
                for player in game.players
            ]
        })

    elif game.status == Game.ONGOING:
        if not player.seen:
            player.seen = True

            try:
                db.session.commit()
            except:
                db.session.rollback()
                raise

        return jsonify(**{
            'id'         : game.id,
            'host'       : {
                'name' : game.host.name,
                'email': game.host.email
            },
            'name'       : game.name,
            'max_points' : game.max_points,
            'max_players': game.max_players,
            'status'     : game.status,
            'black_card' : {
                'id'     : game.black_card.id,
                'text'   : game.black_card.text,
                'answers': game.black_card.answers
            },
            'table'      : [
                {
                    'name' : p.user.name,
                    'email': p.user.email,
                    'cards': [
                        {
                            'id'  : card.id,
                            'text': card.text
                        }
                        for card in p.played
                    ]
                }
                for p in game.players
                if p.played and all(card.answers == 0 for card in p.played)
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
                    'status': player.status,
                    'points': player.score
                }
                for player in game.players
            ],
            'previous'   : game.previous_round
        })

    # TODO
    # elif game.status == Game.ENDED:

    return jsonify(), 404


@app.route('/game/<int:id>/<action>', methods=['POST'])
@with_user
@with_content
def accept_or_decline_game(id, action, user, content):
    game    = Game.get(id)
    player  = Player.get(user, game)
    started = False

    if action == 'add':
        player.set_status_joined()
        joined = [player for player in game.players
                         if player.status == Player.JOINED]

        if len(joined) == game.max_players:
            game.start()
            started = True

    elif action == 'delete':
        player.set_status_denied()

    else:
        return jsonify(), 404

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

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

    game   = Game.get(id)
    player = Player.get(user, game)

    if user == game.judge.user:
        email  = content['email']
        winner = next(
            (player for player in game.players if player.user.email == email),
            None
        )
        winner.add_points(1)
        game.new_round(winner)

    else:

        if player.played:
            return jsonify(), 418

        cards = content['cards']
        map   = {card.id: card for card in player.hand}
        cards = [map[id] for id in cards]
        assert len(cards) == game.black_card.answers

        player.play_cards(cards)

    for p in game.players:
        p.seen = False

    player.seen = True

    try:
        db.session.commit()
    except:
        db.session.rollback()

    return jsonify()
