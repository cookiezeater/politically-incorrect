from models.shared import *

players_to_players = db.Table("p2p", db.Model.metadata,
    db.Column("players_id", db.Integer, db.ForeignKey("players.id")),
    db.Column("players_id", db.Integer, db.ForeignKey("players.id")))


class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    losses = db.Column(db.Integer)

    # One-to-many:
    # A match only has one winner, but a winner can have many won matches.
    hosting = db.relationship("Match", backref="host",
                              foreign_keys="[Match.host_id]")

    # One-to-many:
    # A match only has one winner, but a winner can have many won matches.
    wins = db.relationship("Match", backref="winner",
                           foreign_keys="[Match.winner_id]")

    # Many-to-many:
    # A player has many friends,
    # and any friend can have many friends
    friends = db.relationship("Player", secondary=players_to_players)

    # One-to-many:
    # A player has many states, but a state can only have one player.
    states = db.relationship("State", backref="player")

    def __init__(self,
                 username="",
                 password="",
                 email="",
                 first_name="",
                 last_name=""):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        self.losses = 0
        self.hosting = []
        self.wins = []
        self.friends = []
        self.matches = []
        self.states = []

    def __str__(self):
        return "Player {}: {}".format(self.username, self.email)
