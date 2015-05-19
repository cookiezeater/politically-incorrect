"""
    routes.shared
    ~~~~~
    Contains routes module required imports
    and convenience decorators.
"""

from functools import wraps
from flask import jsonify, request
from common import app, db
from models import (
    Card,
    Game,
    Player,
    User
)


def with_content(func):
    @wraps(func)
    def inner(*args, **kwargs):
        content = request.json
        return func(content, *args, **kwargs)
    return inner


def with_user(func):
    @wraps(func)
    @with_content
    def inner(content, *args, **kwargs):
        token = content['token']
        user  = User.auth(token)
        return func(user, *args, **kwargs)
    return inner
