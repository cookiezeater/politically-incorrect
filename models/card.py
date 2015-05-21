from models.shared import *


class Card(db.Model):
    """A simple card model."""
    __tablename__ = 'cards'

    id      = db.Column(db.Integer, primary_key=True)
    text    = db.Column(db.String(255), nullable=False, unique=True)
    answers = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return '<card id={} text={} answers={}>'.format(
            self.id, self.text, self.answers
        )
