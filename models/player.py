from models.shared import *
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.dialects.postgresql import ARRAY


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    def remove(self, value):
        list.remove(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class Player(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           default=db.func.now(),
                           onupdate=db.func.now())

    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)

    score            = db.Column(db.Integer)
    judged           = db.Column(db.Integer)

    hand = db.Column(MutableList.as_mutable(ARRAY(db.Integer)))
    played = db.Column(MutableList.as_mutable(ARRAY(db.Integer)))

    # Many-to-one:
    # A state has one player, but a player can have many states.
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"))

    # Many-to-one:
    # A state has one match, but a match has many states.
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"))

    # Many-to-many:
    # A state can have several played cards,
    # but a card can have many states in which it is played.

    def __init__(self, player_id=None, match_id=None):
        self.player_id = player_id
        self.match_id = match_id

        self.score = 0
        self.judged = 0
        self.judge = False
        self.round_winner = False
        self.viewed_round_end = False
        self.hand = []
        self.played = []

    def __str__(self):
        played = [str(card) for card in self.played]
        return "State: Player({}) in Match({}) with score({}) and played({})" \
               .format(self.player_id, self.match_id, self.score, str(played))
