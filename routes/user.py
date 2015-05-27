"""
    routes.user
    ~~~~~
    Routes and logic
    for user verification
    and friendship management.
"""

from flask import jsonify

from common import app, db
from util import with_content, with_user
from models import User, Friendship


@app.route('/user', methods=['POST'])
@with_content
def get_user(content):
    token = content['token']
    user  = User.auth(token)
    user  = user if user else User.create(token)

    if not user:
        return jsonify(), 418

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

        if friendship.valid:
            friends.append({
                'name'  : friend.name,
                'email' : friend.email,
                'status': Friendship.VALID
            })

        else:
            if friend == friendship.sender:
                friends.append({
                    'name'  : friend.name,
                    'email' : friend.email,
                    'status': Friendship.REQUEST
                })
            else:
                friends.append({
                    'name'  : friend.name,
                    'email' : friend.email,
                    'status': Friendship.PENDING
                })

    return jsonify(**{
        'name'   : user.name,
        'email'  : user.email,
        'token'  : user.token,
        'friends': friends,
        'games'  : [
            {
                'id'         : player.game.id,
                'name'       : player.game.name,
                'description': player.game.get_description(),
                'status'     : player.game.status,
                'seen'       : player.seen,
                'random'     : player.game.random
            }
            for player in user.players
        ]
    })


@app.route('/user/friend/<action>', methods=['POST'])
@with_user
@with_content
def accept_or_decline_friend(action, user, content):
    email = content['email']
    other = User.get(email)

    if not other:
        return jsonify(), 418

    if action == 'add':
        user.add(other)

    elif action == 'delete':
        user.delete(other)

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
    query   = content['query']
    results = User.search(query)

    friendships = user.get_friendships()
    friends  = set(friendship.sender for friendship in friendships)
    friends |= set(friendship.receiver for friendship in friendships)

    results = [result for result in results if result not in friends | set([user]) ]

    return jsonify(results=[
        {
            'name' : user.name,
            'email': user.email
        }
        for user in results
    ])
