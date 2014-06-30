from models.shared import *

states_to_cards = db.Table("s2c", db.Model.metadata,
    db.Column("states_id", db.Integer, db.ForeignKey("states.id")),
    db.Column("cards_id", db.Integer, db.ForeignKey("cards.id")))


class State(db.Model):
    __tablename__ = "states"
    id = db.Column(db.Integer, primary_key=True)

    score = db.Column(db.Integer)
    judged = db.Column(db.Integer)
    judge = db.Column(db.Boolean)
    round_winner = db.Column(db.Boolean)
    viewed_round_end = db.Column(db.Boolean)

    # Many-to-one:
    # A state has one player, but a player can have many states.
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"))

    # Many-to-one:
    # A state has one match, but a match has many states.
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"))

    # Many-to-many:
    # A state has a hand with many cards,
    # and cards can belong to many hands in many states.
    hand = db.relationship("Card", secondary=states_to_cards)

    # Many-to-one:
    # A state has one played card,
    # but a card can have many states in which it is played.
    played_id = db.Column(db.Integer, db.ForeignKey("cards.id"))

    def __init__(self, player_id=None, match_id=None):
        self.player_id = player_id
        self.match_id = match_id

        self.score = 0
        self.judged = 0
        self.judge = False
        self.round_winner = False
        self.viewed_round_end = False
        self.hand = []
        self.played_id = None

    def __str__(self):
        return "State: Player({}) in Match({}) \
                with score({})".format(self.player_id,
                                       self.match_id,
                                       self.score)
