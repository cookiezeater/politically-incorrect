from models.card import Card
from models.player import FriendshipManager, Player
from models.state import State
from models.match import Match
from models.shared import app, db
from flask.ext.httpauth import HTTPBasicAuth
from flask import jsonify, request, g

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password_or_token):
    player = Player.verify_auth_token(password_or_token)
    if player:
        assert player.username == username, "Invalid username."
    else:
        player = Player.query.filter_by(username=username).first()
        if not player:
            return False
        if player.verify_password(password_or_token):
            pass
        else:
            return False
    g.player = player
    return True


def jsonify_assertion_error(func):
    def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AssertionError as error:
                return jsonify(status="failure", message=error)
    return wrapper


def get_player(username, password=None):
    player = Player.query.filter_by(username=username).first()
    if not player:
        assert False, "Invalid username."
    if password:
        assert password == player.password, "Invalid password."
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
