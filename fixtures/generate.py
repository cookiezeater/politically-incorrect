#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import json

from app import db
from models import *


def add_cards():
    with open('cards/black.txt') as black, \
         open('cards/white.txt') as white:
        black_text = list(set(black.readlines()))
        white_text = list(set(white.readlines()))

    white_cards = [
        Card(text=text.strip(), answers=0) for text in white_text
    ]
    black_cards = [
        Card(text=text.strip(), answers=max(text.count('████'), 1)) for text in black_text
    ]
    db.session.add_all(white_cards + black_cards)
    db.session.commit()


def add_users():
    with open('fixtures/users.json') as users:
        users = json.loads(users.read())

    users = [
        User(token=User.generate_auth_token(user['email']), num_random=0, **user)
        for user in users
    ]
    db.session.add_all(users)
    db.session.commit()


if __name__ == '__main__':
    add_cards()
    add_users()
