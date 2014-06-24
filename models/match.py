from models.shared import *

matches_to_players = db.Table('m2p', db.Model.metadata,
    db.Column('matches_id', db.Integer, db.ForeignKey('matches.id')),
    db.Column('players_id', db.Integer, db.ForeignKey('players.id')))

matches_to_cards = db.Table('m2c', db.Model.metadata,
    db.Column('matches_id', db.Integer, db.ForeignKey('matches.id')),
    db.Column('cards_id', db.Integer, db.ForeignKey('cards.id')))


class Match(db.Model):
    STATUSES = "PENDING", "ONGOING", "ENDED"

    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(7))

    # One-to-many:
    # A match has many states, but a state can only have one match.
    states = db.relationship('State', backref='match')

    # Many-to-many:
    # A match can have many pending players,
    # and a pending player can have many pending matches.
    pending = db.relationship("Player", secondary=matches_to_players)

    # Many-to-one:
    # A match only has one winner, but a winner can have many won matches.
    winner_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    # Many-to-many:
    # A match has many cards in a deck,
    # and cards can have many decks in many matches.
    deck = db.relationship("Card", secondary=matches_to_cards)

    # Many-to-one:
    # A match has one black card at any time,
    # but a black card can be in many matches.
    black_id = db.Column(db.Integer, db.ForeignKey('cards.id'))

    def __init__(self,
                 host=None,
                 status="PENDING",
                 state=None,
                 pending=[],
                 table=None,
                 winner_id=-1,
                 winner=None):
        raise NotImplementedError

    def __str__(self):
        players = "get_all_players"
        raise NotImplementedError
        return "Match players: {}, status: {}, judge: {}".format(
            players, self.status, self.judge)
