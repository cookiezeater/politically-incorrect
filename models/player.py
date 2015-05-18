"""
    models.player
    ~~~~~
    Player model, which represents
    a user's state inside a game.
"""

from models.shared import *


class Player(Base):
    """
    Player model containing
    functions which encapsulate
    gameplay state changes.

    columns
    ~~~~~
    | status | score | judged |
    |--------|-------|--------|
    | str    | int   | int

    relationships
    ~~~~~
    user  : user   <-  player
    game  : game   <-  player
    hand  : player  -  card
    played: player  -  card
    """

    STATUSES = ('PENDING', 'JOINED')

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    user    = relationship('User', uselist=False, back_populates='players')
    game    = relationship('Game', uselist=False, back_populates='players')
    status  = db.Column(db.String(10), nullable=False)
    score   = db.Column(db.Integer)
    judged  = db.Column(db.Integer)
    hand    = relationship('Card')
    played  = relationship('Card')
