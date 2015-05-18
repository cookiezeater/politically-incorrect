"""
    routes.user
    ~~~~~
    Routes and logic
    for user verification
    and friendship management.
"""

from routes.shared import *


@app.route('/user', methods=['POST'])
@with_content
def get(content):
    token = content['token']
    user  = User.auth(token)

    if not user:
        user = User.create(token)

    friends = User.get_friends()

    return jsonify(**{
        'name'   : user.name,
        'email'  : user.email,
        'token'  : user.token,
        'friends': [
            {
                'name' : friend.name,
                'email': friend.email
            }
            for friend in friends
        ],
        'games'  : [
            {
                'id'    : player.game.id,
                'name'  : player.game.name,
                'state' : player.game.state,
                'seen'  : player.seen,
                'random': player.game.random
            }
            for player in user.players
        ]
    }


@app.route('/user/friends/<action>', methods=['POST'])
@with_user
@with_content
def accept_or_decline(user, content):
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

    return jsonify()


@app.route('/user/friends/search', methods=['POST'])
@with_user
@with_content
def search(user, content):
    query  = content['query']
    result = User.search(query)

    return jsonify(result=[
        {
            'name' : user.name,
            'email': user.email
        }
        for user in result
    ])
