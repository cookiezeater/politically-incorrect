"""
    routes.game
    ~~~~~
    Endpoints and controller
    logic for gameplay.
"""

from flask import jsonify

from common import app, db
from util import notify, with_content, with_user
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
    max_points  = max(content['max_points'], 5)
    max_players = content['max_players']
    random      = content['random']
    emails      = content['emails']

    if len(emails) < 3:
        return jsonify(message='You need to invite more people!'), 418

    game = Game.create(
        user, name, max_points, min(max_players, len(emails) + 1), random
    )
    users   = User.get_all(emails) + [user]
    players = Player.create_all(users, game)

    player = next(
        (player for player in players if player.user == user),
        None
    )
    player.set_status_joined()

    notify(
        [u.device for u in users if u != user],
        'Politically Incorrect',
        'You\'ve been invited to a game: "{}"!'.format(name)
    )

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
                'name'  : p.user.name,
                'email' : p.user.email,
                'status': p.status
            }
            for p in game.players
        ]
    })


@app.route('/game/<int:id>/invite', methods=['POST'])
@with_user
@with_content
def invite(id, user, content):
    """Invites a list of users."""
    game = Game.get(id)

    if not (user == game.host and game.status == Game.PENDING):
        return jsonify(message='I can\'t let you do that, Dave.'), 418

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
    """Returns a game in a format dependent on the game's status."""
    game   = Game.get(id)
    player = Player.get(user, game)

    if player not in [p for p in game.players if p.status != Player.REJECTED]:
        return jsonify(
            message='You can\'t see this game because you\'re not in it!'
        ), 418

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
                    'name'   : p.user.name,
                    'email'  : p.user.email,
                    'picture': p.user.picture,
                    'status' : p.status,
                    'points' : 0
                }
                for p in game.players
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
                    'name'   : p.user.name,
                    'email'  : p.user.email,
                    'picture': p.user.picture,
                    'cards'  : [
                        {
                            'id'  : card.id,
                            'text': card.text
                        }
                        for card in p.get_played()
                    ]
                }
                for p in game.players
                if p.played and p != game.judge
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
                    'name'   : p.user.name,
                    'email'  : p.user.email,
                    'picture': p.user.picture,
                    'status' : p.status,
                    'points' : p.score
                }
                for p in game.players
            ],
            'previous'   : game.previous_round
        })

    elif game.status == Game.ENDED:
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
                    'name'   : p.user.name,
                    'email'  : p.user.email,
                    'picture': p.user.picture,
                    'status' : p.status,
                    'points' : p.score
                }
                for p in game.players
            ],
            'previous'   : game.previous_round
        })

    return jsonify(), 418


@app.route('/game/random', methods=['POST'])
@with_user
def join_random(user):
    """Finds and joins the optimal random game."""
    if user.num_random > 4:
        return jsonify(), 418

    game = Game.find_random(user)

    if not game:
        return jsonify(), 418

    player = Player.create(user, game)
    player.set_status_joined()
    user.num_random += 1

    joined = [p for p in game.players
                if p.status == Player.JOINED]

    if len(joined) == game.max_players:
        game.start()

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return jsonify()


@app.route('/game/<int:id>/<action>', methods=['POST'])
@with_user
@with_content
def accept_or_decline_game(id, action, user, content):
    """Join/invite/decline actions for games."""
    game    = Game.get(id)
    player  = Player.get(user, game)
    started = False

    if action == 'add':
        player.set_status_joined()
        joined = [p for p in game.players
                    if p.status == Player.JOINED]

        if len(joined) == game.max_players:
            notify(
                [p.user.device for p in game.players if p.user.device and p != player],
                'Politically Incorrect',
                'The game "{}" has started!'.format(game.name)
            )
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
    the request body should contain card ids in the
    user's hand, which should be placed on the table.

    request :=
        POST ({
            'cards': [int]
        } | {
            'email': str
        })
    """

    game   = Game.get(id)
    player = Player.get(user, game)

    if game.status != Game.ONGOING:
        return jsonify(message='This game isn\'t in-progress.'), 418

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
        cards = [map[card] for card in cards]

        if len(cards) != game.black_card.answers:
            return jsonify(message='Invalid play, mate.'), 418

        player.play_cards(cards)

    notify(
        [p.user.device for p in game.players if p.user.device and p != player],
        'Politically Incorrect',
        'Something happened in "{}"!'.format(game.name)
    )

    for p in game.players:
        p.seen = False

    player.seen = True

    try:
        db.session.commit()
    except:
        db.session.rollback()

    return jsonify()
