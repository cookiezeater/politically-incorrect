import sys
from models.shared import *
from passlib.apps import custom_app_context
from validate_email import validate_email


class FriendshipManager(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(
            db.DateTime,
            default=db.func.now(),
            onupdate=db.func.now()
    )

    __tablename__ = "friendship_manager"
    id = db.Column(db.Integer, primary_key=True)

    sender   = db.Column(db.Integer)
    receiver = db.Column(db.Integer)
    valid    = db.Column(db.Boolean, default=False)

    def __init__(self, sender, receiver, vaild=False):
        self.sender   = sender
        self.receiver = receiver
        self.valid    = valid


class User(db.Model):
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(
            db.DateTime,
            default=db.func.now(),
            onupdate=db.func.now()
    )

    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(64), unique=True)

    # One-to-many:
    # A match only has one winner, but a winner can have many won matches.
    wins = db.relationship(
            "Match",
            backref="winner",
            foreign_keys="[Match.winner_id]"
    )

    # One-to-many:
    # A user has many states, but a state can only have one user.
    states = db.relationship(
            "State",
            backref="user",
            foreign_keys="[State.user_id]"
    )

    def __init__(self, email, token):
        assert validate_email(email)

        self.email  = email
        self.wins   = []
        self.states = []

    def generate_auth_token(self, expiration=sys.maxint):
        cereal = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
        return cereal.dumps({ "id": self.id })

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
        user = User.query.get(data["id"])
        return user

    def __str__(self):
        return "user {}".format(self.email)
