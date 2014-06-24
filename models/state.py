from models.shared import *

states_to_cards = db.Table('s2c', db.Model.metadata,
    db.Column('states_id', db.Integer, db.ForeignKey('states.id')),
    db.Column('cards_id', db.Integer, db.ForeignKey('cards.id')))


class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)

    score = db.Column(db.Integer)
    judged = db.Column(db.Integer)

    # Many-to-one:
    # A state has one player, but a player can have many states.
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    # Many-to-one:
    # A state has one match, but a match has many states.
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

    # Many-to-many:
    # A state has a hand with many cards,
    # and cards can belong to many hands in many states.
    hand = db.relationship("Card", secondary=states_to_cards)

    # Many-to-one:
    # A state has one played card,
    # but a card can have many states in which it is played.
    played_id = db.Column(db.Integer, db.ForeignKey('cards.id'))

    def __init__(self, player=None, match=None, score=0,
                 hand=[], played=None, judged=0):
        raise NotImplementedError

    def __str__(self):
        return "State: Player {}, Match {}".format(self.player, self.match)
