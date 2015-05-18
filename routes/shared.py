"""
    routes.shared
    ~~~~~
    Contains routes module required imports
    and convenience decorators.
"""

from models.shared import app
from functools import wraps
from flask import jsonify, request


def with_content(func):
    @wraps
    def inner(*args, **kwargs):
        content = request.json
        return func(content, *args, **kwargs)
    return inner


def with_user(func):
    @wraps
    @with_content
    def inner(content, *args, **kwargs):
        token = content['token']
        user  = User.auth(token)
        return func(user, *args, **kwargs)
    return inner
