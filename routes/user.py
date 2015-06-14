"""
    routes.user
    ~~~~~
    Routes and logic
    for user verification
    and friendship management.
"""

from flask import jsonify
from datetime import datetime, timedelta

from common import app, db
from util import notify, with_content, with_user
from models import Friendship, Game, Player, User


@app.route('/user', methods=['POST'])
@with_content
def get_user(content):
    """
    Find and return the user's info, or
    create the user if he doesn't exist.
    If the user doesn't exist, enter
    the user into 3 random games and
    add 5 random friends.
    """

    token  = content['token']
    device = content['device']
    now    = datetime.now()
    user   = User.auth(token)

    if not user:
        user = User.create(token)

        if not user:
            return jsonify(), 418

        else:  # give the new user 3 random games and 5 random friends
            games   = Game.find_n_random(3, user)
            players = [Player.create(user, game) for game in games]
            [player.set_status_joined() for player in players]

            for game in games:
                joined = [p for p in game.players
                            if p.status == Player.JOINED]
                if len(joined) == game.max_players:
                    game.start()

            friends = User.find_n_random(5, user)
            [f.add(user) for f in friends]
            [user.add(f) for f in friends]

    user.device = device

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    friendships = user.get_friendships()
    friends     = []

    for friendship in friendships:
        friend = \
            friendship.sender if friendship.sender != user else \
            friendship.receiver

        friend_json = {
            'name'   : friend.name,
            'email'  : friend.email,
            'picture': friend.picture
        }

        if friendship.valid:
            friend_json['status'] = Friendship.VALID
        elif friend == friendship.sender:
            friend_json['status'] = Friendship.REQUEST
        else:
            friend_json['status'] = Friendship.PENDING

        friends.append(friend_json)

    return jsonify(**{
        'name'   : user.name,
        'email'  : user.email,
        'picture': user.picture,
        'token'  : user.token,
        'friends': friends,
        'games'  : [
            {
                'id'           : p.game.id,
                'name'         : p.game.name,
                'status'       : p.game.status,
                'player_status': p.status,
                'seen'         : p.seen,
                'random'       : p.game.random,
                'players'      : [
                    {
                        'name'   : _p.user.name,
                        'email'  : _p.user.email,
                        'picture': _p.user.picture,
                        'status' : _p.status,
                        'points' : _p.score
                    }
                    for _p in p.game.players
                ]
            }
            for p in user.players
            if not p.game.end_time or p.game.end_time + timedelta(weeks=1) > now
        ]
    })


@app.route('/user/friend/<action>', methods=['POST'])
@with_user
@with_content
def accept_or_decline_friend(action, user, content):
    """Request/accept/decline friend requests."""
    emails = content['emails']
    others = User.get_all(emails)

    if not others:
        return jsonify(), 418

    if action == 'add':
        [user.add(other) for other in others]

        if other.device:
            notify(
                [other.device],
                'Politically Incorrect',
                '{} added you as a friend!'.format(user.name)
            )

    elif action == 'delete':
        [user.delete(other) for other in others]

    else:
        return jsonify(), 404

    try:
        db.session.commit()
    except:
        db.session.rollback()
        raise

    return jsonify()


@app.route('/user/friend/search', methods=['POST'])
@with_user
@with_content
def search(user, content):
    """Super naive search on users."""
    query   = content['query']
    results = User.search(query)

    friendships = user.get_friendships()
    friends     = set(friendship.sender for friendship in friendships)
    friends    |= set(friendship.receiver for friendship in friendships)
    friends    |= set([user])

    results = [result for result in results if result not in friends]

    return jsonify(results=[
        {
            'name'   : u.name,
            'email'  : u.email,
            'picture': u.picture
        }
        for u in results
    ])
