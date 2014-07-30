from models.card import Card
from models.player import FriendshipManager, Player
from models.state import State
from models.match import Match
from models.shared import app, db
from flask.ext.httpauth import HTTPBasicAuth
from flask import jsonify, request, g

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username_or_token, password):
    player = Player.verify_auth_token(username_or_token)
    if not player:
        player = Player.query.filter_by(username=username_or_token).first()
        if not player or not player.verify_password(password):
            return False
    g.player = player
    return True


def jsonify_assertion_error(func):
    def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AssertionError as error:
                return jsonify(status="fail", message=error)
    return wrapper


def get_player(player_id, password=None):
    player = Player.query.get_or_404(player_id)
    if password:
        assert password == player.password, "Invalid password."
    return player


def get_state(player_id, match_id):
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
