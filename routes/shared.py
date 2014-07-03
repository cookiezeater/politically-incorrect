from models.card import Card
from models.player import FriendshipManager, Player
from models.state import State
from models.match import Match
from models.shared import app, db
from flask import jsonify, request

def catch_assertion_error(func):
    def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except AssertionError as ass:
                return jsonify(status="failure", message=ass)
    return wrapper
