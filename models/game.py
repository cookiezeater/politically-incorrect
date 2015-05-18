"""
    models.game
    ~~~~~
    Game model, containing
    information about
    individual games.
"""

from models.shared import *


class Game(Base):
    STATUSES = ('PENDING', 'ONGOING', 'ENDED')

    name        = db.Column(db.String(80))
    max_points  = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    status      = db.Column(db.String(7))
