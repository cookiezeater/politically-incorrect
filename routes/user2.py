from routes.shared import *


@app.route('/user', methods=['POST'])
def get():
    content = request.json
    token   = content['token']
    user    = User.auth(token)

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
def accept_or_decline(user):
    content = request.json
    email   = content['email']
    other   = User.get(email)

    if not other:
        return jsonify(message='User does not exist.'), 418

    if action == 'add':
        user.add(other)

    elif action == 'delete':
        user.delete(other)

    else:
        return jsonify(message='Invalid route.'), 404

    return jsonify(), 200


@app.route('/user/friends/search', methods=['POST'])
@with_user
def search(user):
    content = request.json
    query   = content['query']
    result  = [
        {
            'name' : user.name,
            'email': user.email
        }
        for user in User.search(query)
    ]
    return jsonify(result=result), 200
