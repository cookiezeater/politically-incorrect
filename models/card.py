from models.shared import *


class Card(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           default=db.func.now(),
                           onupdate=db.func.now())

    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.String(120), unique=True)
    white = db.Column(db.Boolean)
    answers = db.Column(db.Integer)
    rank = db.Column(db.Integer)
    meta = db.Column(db.String(500))

    # One-to-many:
    # A match has one black card at any time,
    # but a black card can be in many matches.
    matches = db.relationship("Match", backref="cards")

    def __init__(self, text=None, white=True, answers=1,
                 rank=0, meta="", matches=[]):
        self.text = text
        self.white = white

        if self.white:
            self.answers = 0
        else:
            self.answers = answers
        self.rank = rank
        self.meta = meta
        if matches is None:
            self.matches = []
        else:
            self.matches = matches

    def __str__(self):
        if self.white:
            return "{}: {}".format("White", self.text)
        else:
            return "{}({}): {}".format("Black", self.answers, self.text)

    def __eq__(self, other):
        return self.id == other.id
