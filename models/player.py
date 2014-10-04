import sys
from models.shared import *
from passlib.apps import custom_app_context
from validate_email import validate_email


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

    player_type = db.Column(db.String(32))
    username = db.Column(db.String(32), unique=True)
    password = db.Column(db.String(256), default=None)
    email = db.Column(db.String(128), unique=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))

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

    def __init__(self,
                 player_type,
                 username,
                 email,
                 password,
                 first_name,
                 last_name):
        self.player_type = player_type

        if username.isalnum():
            self.username = username
        elif player_type == "google":
            self.username = username
        else:
            assert False, "Invalid characters in username."

        if validate_email(email):
            self.email = email
        else:
            assert False, "Invalid email."

        if password is None:
            self.password = None
        else:
            self.password = self.hash_password(password)

        if first_name.isalnum():
            self.first_name = first_name
        else:
            assert False, "Invalid first name."

        if last_name.isalnum():
            self.last_name = last_name
        else:
            assert False, "Invalid last name."

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
