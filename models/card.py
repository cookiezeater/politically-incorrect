from models.shared import *


class Card(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(
            db.DateTime,
            default=db.func.now(),
            onupdate=db.func.now()
    )

    __tablename__ = "cards"
    id = db.Column(db.Integer, primary_key=True)

    text    = db.Column(db.String(120), unique=True)
    white   = db.Column(db.Boolean)
    answers = db.Column(db.Integer)

    def __init__(self, text, white, answers=1):
        self.text    = text
        self.white   = white
        self.answers = 0 if self.white else answers

    def __str__(self):
        return "White: {}".format(self.text) if self.white else \
               "Black({}): {}".format(self.answers, self.text)

    def __eq__(self, other):
        return self.id == other.id
