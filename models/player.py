from models.shared import *


class FriendshipManager(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           default=db.func.now(),
                           onupdate=db.func.now())

    __tablename__ = "friendship_manager"
    id = db.Column(db.Integer, primary_key=True)

    requester = db.Column(db.Integer)
    requestee = db.Column(db.Integer)
    accepted = db.Column(db.Boolean, default=False)

    def __init__(self, requester, requestee, accepted=False):
        self.requester = requester
        self.requestee = requestee
        self.accepted = accepted


class Player(db.Model):
    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(32))
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    # One-to-many:
    # A match only has one winner, but a winner can have many won matches.
    hosting = db.relationship("Match",
                              backref="host",
                              foreign_keys="[Match.host_id]")

    # One-to-many:
    # A match only has one winner, but a winner can have many won matches.
    wins = db.relationship("Match",
                           backref="winner",
                           foreign_keys="[Match.winner_id]")

    # One-to-many:
    # A player has many states, but a state can only have one player.
    states = db.relationship("State",
                             backref="player",
                             foreign_keys="[State.player_id]")

    def __init__(self, username, password, email, first_name, last_name):
        self.username = username
        self.password = password
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        self.hosting = []
        self.wins = []
        self.states = []
        self.friends = []
        self.pending_friends = []

    def __str__(self):
        return "Player {}: {}".format(self.username, self.email)
