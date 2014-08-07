import sys
from models.shared import *
from passlib.apps import custom_app_context
from itsdangerous import SignatureExpired, BadSignature
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


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
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime,
                           default=db.func.now(),
                           onupdate=db.func.now())

    __tablename__ = "players"
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256))
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

    def __init__(self, username, email, password, first_name, last_name):
        self.username = username
        self.email = email
        self.password = self.hash_password(password)
        self.first_name = first_name
        self.last_name = last_name

        self.hosting = []
        self.wins = []
        self.states = []
        self.friends = []
        self.pending_friends = []

    def __str__(self):
        return "Player {}: {}".format(self.username, self.email)

    def hash_password(self, password):
        return custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    def generate_auth_token(self, expiration=sys.maxint):
        cereal = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
        return cereal.dumps({"id": self.id})

    @staticmethod
    def verify_auth_token(token):
        cereal = Serializer(app.config["SECRET_KEY"])
        try:
            data = cereal.loads(token)
        except SignatureExpired:
            # Valid but expired token
            return None
        except BadSignature:
            # Invalid token
            return None
        if data["id"] is None:
            return None
        player = Player.query.get(data["id"])
        return player
