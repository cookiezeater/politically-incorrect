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

    result = {
        'name' : user.name,
        'email': user.email,
        'token': user.token,
        'games': games
    }
    return jsonify(**result)


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

    return jsonify(), 200


@app.route('/user/friends/search', methods=['POST'])
@with_user
@with_content
def search(user, content):
    query  = content['query']
    result = [
        {
            'name' : user.name,
            'email': user.email
        }
        for user in User.search(query)
    ]
    return jsonify(result=result), 200
