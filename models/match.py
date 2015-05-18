from models.shared import *

games_to_users = db.Table("m2p", db.Model.metadata,
        db.Column("games_id", db.Integer, db.ForeignKey("games.id")),
        db.Column("users_id", db.Integer, db.ForeignKey("users.id"))
    )

games_to_cards = db.Table("m2c", db.Model.metadata,
        db.Column("games_id", db.Integer, db.ForeignKey("games.id")),
        db.Column("cards_id", db.Integer, db.ForeignKey("cards.id"))
    )


class Game(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(
            db.DateTime,
            default=db.func.now(),
            onupdate=db.func.now()
    )

    STATUSES = "PENDING", "ONGOING", "ENDED"

    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True)

    name        = db.Column(db.String(80))
    max_points  = db.Column(db.Integer)
    max_players = db.Column(db.Integer)
    status      = db.Column(db.String(7))

    # One-to-many:
    # A match has many states, but a state can only have one match.
    states = db.relationship(
            "State",
            backref="match",
            foreign_keys="[State.match_id]"
    )

    # Many-to-one:
    # A match only has one winner, but a winner can have many won games.
    winner = db.Column(db.Integer, db.ForeignKey("users.id"))

    # Many-to-many:
    # A match has many cards in a deck,
    # and cards can have many decks in many games.
    deck = db.relationship("Card", secondary=games_to_cards)

    # Many-to-one:
    # A match has one black card at any time,
    # but a black card can be in many games.
    black = db.Column(db.Integer, db.ForeignKey("cards.id"))

    # Pickle
    # I'm getting lazy
    previous_round = db.Column(db.PickleType)

    def __init__(self, name, host_id, max_players, max_points):
        self.name        = name
        self.max_points  = max_points
        self.max_players = max_players

        self.status         = "PENDING"
        self.states         = []
        self.winner         = None
        self.deck           = []
        self.black          = None
        self.previous_round = None

    def __str__(self):
        return "Match {}".format(self.id)
