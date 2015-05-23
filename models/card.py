"""
    models.card
    ~~~~~
    A card model. Not
    much else to say
    here...
"""

from common import db


class Card(db.Model):
    """A simple card model."""
    __tablename__ = 'cards'

    id      = db.Column(db.Integer, primary_key=True)
    text    = db.Column(db.String(255), nullable=False, unique=True)
    answers = db.Column(db.Integer, nullable=False)

    @staticmethod
    def get_all(black=False):
        if black:
            query = Card.answers > 0
        else:
            query = Card.answers == 0
        return Card.query.filter(query).all()

    def __repr__(self):
        return '<card id={} answers={}>'.format(
            self.id, self.answers
        )
