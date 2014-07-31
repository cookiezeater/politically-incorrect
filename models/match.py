from models.shared import *

matches_to_players = db.Table("m2p", db.Model.metadata,
    db.Column("matches_id", db.Integer, db.ForeignKey("matches.id")),
    db.Column("players_id", db.Integer, db.ForeignKey("players.id")))

matches_to_cards = db.Table("m2c", db.Model.metadata,
    db.Column("matches_id", db.Integer, db.ForeignKey("matches.id")),
    db.Column("cards_id", db.Integer, db.ForeignKey("cards.id")))


class Match(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           default=db.func.now(),
                           onupdate=db.func.now())

    STATUSES = "PENDING", "ONGOING", "ENDED"

    __tablename__ = "matches"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(80))
    status = db.Column(db.String(7))
    max_players = db.Column(db.Integer)
    max_score = db.Column(db.Integer)

    # Many-to-one:
    # A match only has one host, but a host can have many matches.
    host_id = db.Column(db.Integer, db.ForeignKey("players.id"))

    # One-to-many:
    # A match has many states, but a state can only have one match.
    states = db.relationship("State",
                             backref="match",
                             foreign_keys="[State.match_id]")

    # Many-to-many:
    # A match can have many pending players,
    # and a pending player can have many pending matches.
    pending = db.relationship("Player",
                              backref="invited",
                              secondary=matches_to_players)

    # Many-to-one:
    # A match only has one winner, but a winner can have many won matches.
    winner_id = db.Column(db.Integer, db.ForeignKey("players.id"))

    # Many-to-many:
    # A match has many cards in a deck,
    # and cards can have many decks in many matches.
    deck = db.relationship("Card", secondary=matches_to_cards)

    # Many-to-one:
    # A match has one black card at any time,
    # but a black card can be in many matches.
    black_id = db.Column(db.Integer, db.ForeignKey("cards.id"))

    # Pickle
    # I'm getting lazy
    previous_round = db.Column(db.PickleType)

    def __init__(self, name, host_id, max_players, max_score):
        self.name = name
        self.host_id = host_id
        self.max_players = max_players
        self.max_score = max_score

        self.status = "PENDING"
        self.states = []
        self.pending = []
        self.winner_id = None
        self.deck = []
        self.black_id = None

    def __str__(self):
        return "Match {}".format(self.id)
