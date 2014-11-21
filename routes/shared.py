from functools import wraps
from models.card import Card
from models.player import FriendshipManager, Player
from models.state import State
from models.match import Match
from models.shared import app, db
from flask.ext.httpauth import HTTPBasicAuth
from flask import jsonify, request, g

auth = HTTPBasicAuth()


@auth.verify_password
def verify_token(username, token):
    player = Player.verify_auth_token(token)
    if player:
        assert player.username == username, "Invalid auth."
    else:
        return False
    g.player = player
    return True


def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.authorization and auth.username() == "charles":
            return func(*args, **kwargs)
        else:
            assert False, "You don't have permission to do that."
    return wrapper


def jsonify_assertion_error(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AssertionError as error:
            app.logger.exception(error)
            return jsonify(status="failure", message=error.message), 418
        except Exception as error:
            app.logger.exception(error)
            return 500
    return wrapper


def get_player(username, password=None):
    player = Player.query.filter_by(username=username).first()
    if not player:
        assert False, "Invalid user."
    if password:
        assert password == player.password, "Invalid user."
    return player


def get_state(username_or_id, match_id):
    if type(username_or_id) is unicode:
        player_id = Player.query.filter_by(username=username_or_id).first().id
    elif type(username_or_id) is int:
        player_id = username_or_id
    state = State.query.filter_by(player_id=player_id, match_id=match_id)
    try:
        return state.first()
    except:
        assert False, "Invalid player or match."


def get_match(match_id):
    match = Match.query.get_or_404(match_id)
    return match


def get_judge_state(match_id):
    judge_state = State.query.filter_by(match_id=match_id, judge=True)
    try:
        return judge_state.first()
    except:
        return None


def get_round_winner_state(match_id):
    round_winner_state = State.query.filter_by(match_id=match_id,
                                               round_winner=True)
    try:
        return round_winner_state.first()
    except:
        return None
