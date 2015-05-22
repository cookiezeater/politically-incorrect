"""
    routes.util
    ~~~~~
    Shared util functions
    for routes.
"""

from functools import wraps
from flask import request

from models import User


def with_content(func):
    @wraps(func)
    def inner(*args, **kwargs):
        content = request.json
        return func(content=content, *args, **kwargs)
    return inner


def with_user(func):
    @wraps(func)
    @with_content
    def inner(content, *args, **kwargs):
        token = content['token']
        user  = User.auth(token)
        return func(user=user, *args, **kwargs)
    return inner
