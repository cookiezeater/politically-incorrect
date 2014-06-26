from models.shared import *


class Card(db.Model):
    """
    Represents a player-made card. Scaffold should contain
    default Cards Against Humanity cards for testing purposes.
    """

    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.String(120), unique=True)
    white = db.Column(db.Boolean)
    rank = db.Column(db.Integer)
    meta = db.Column(db.String(500))

    # One-to-many:
    # A match has one black card at any time,
    # but a black card can be in many matches.
    matches = db.relationship('Match', backref='cards')

    def __init__(self, text=None, white=True, rank=0, meta="", matches=[]):
        self.text = text
        self.white = white

        self.rank = rank
        self.meta = meta
        if matches is None:
            self.matches = []
        else:
            self.matches = matches

    def __str__(self):
        return "{} Card: {}".format("White" if self.white else "Black",
                                    self.text)
