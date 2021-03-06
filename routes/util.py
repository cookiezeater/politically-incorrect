"""
    routes.util
    ~~~~~
    Shared util functions
    for routes.
"""

import os
import json
import requests
from functools import wraps
from flask import request

from models import User

GCM_URL = 'https://gcm-http.googleapis.com/gcm/send'
GCM_KEY = os.getenv('GCM_KEY', '').strip()


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


def notify(devices, title, text):
    headers = {
        'Authorization': 'key={}'.format(GCM_KEY),
        'Content-Type' : 'application/json'
    }
    body = {
        'data': {
            'title': title,
            'text' : text
        },
        'registration_ids': devices
    }

    # TODO: log this
    response = requests.post(GCM_URL, headers=headers, data=json.dumps(body))
    return response
