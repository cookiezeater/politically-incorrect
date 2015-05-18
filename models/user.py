"""
    models.user
    ~~~~~
    User model and model-level
    functions. Encapsulates
    and abstracts access and
    modification functions
    of the user store.
"""

from models.shared import *

TOKEN_EXPIRATION = 696969696969
GOOGLE_URL = \
        "https://www.googleapis.com/oauth2/v1/userinfo?access_token="


class User(Base):
    """
    A sqlalchemy model representing the user.
    Most information is obtained
    from Google oauth on user creation.

    columns
    ~~~~~
    | name | email | picture | token |
    |------|-------|---------|-------|
    | str  | str   | str     | str   |

    relationships
    ~~~~~
    friends: user <-> user
    players: user <-> game
    """

    name    = db.Column(db.String(128), nullable=False)
    email   = db.Column(db.String(128), nullable=False, unique=True)
    picture = db.Column(db.String(255), nullable=False)
    token   = db.Column(db.String(255), nullable=False)

    @staticmethod
    def create(oauth_token):
        """Create and return a new user."""
        response = requests.get(GOOGLE_URL.format(oauth_token))
        name     = response['given_name'] + ' ' + response['family_name']
        email    = response['email']
        picture  = response['picture']
        user     = User(
            name=name, email=email, picture=picture, token=generate_auth_token()
        )
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def get(email):
        """Get an existing user by email."""
        return User.query.get(email=email)

    @staticmethod
    def auth(token):
        """Authorize and return an existing user."""
        cereal = Serializer(app.config["SECRET_KEY"])
        try:
            data = cereal.loads(token)
        except SignatureExpired:
            # valid but expired token
            return None
        except BadSignature:
            # invalid token
            return None
        if "email" not in data or data["email"] is None:
            return None
        user = User.query.get(email=data["email"])
        return user

    @staticmethod
    def generate_auth_token(email, expiration=TOKEN_EXPIRATION):
        """Generate an auth token from a user's email."""
        cereal = Serializer(app.config["SECRET_KEY"], expires_in=expiration)
        return cereal.dumps({ "email": self.email })

    @staticmethod
    def search(query):
        """Naive ILIKE search on name and email columns."""
        words    = query.split(' ')
        or_query = []

        for word in words:
            like = '%{}%'.format(word)
            or_query.append(User.name.ilike(like))
            or_query.append(User.email.ilike(like))

        return User.query.like(or_(*or_query)).all()

    def add(self, other):
        """Creates a friendship request or validates an existing one."""
        friendship = Friendship.get(self, other)
        if friendship:
            friendship.set_valid(True)
        else:
            Friendship.create(self, other)

    def remove(self, other):
        """Sets an friendship to invalid."""
        friendship = Friendship.get(self, other)
        if friendship:
            friendship.set_valid(False)

    def __repr__(self):
        return "<User {}>".format(self.email)


class Friendship(Base):
    """A simple table of one-to-one friendships."""
    sender_id   = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    valid       = db.Column(db.Boolean, nullable=False, default=False)

    sender   = relationship('User')
    receiver = relationship('User')

    __table_args__ = (UniqueConstraint('sender_id', 'receiver_id'))

    @staticmethod
    def create(sender, receiver):
        assert not Friendship.get(sender, receiver)
        friendship = Friendship(sender_id=sender.id, receiver_id=receiver.id)
        db.session.add(friendship)
        db.session.commit()
        return friendship

    @staticmethod
    def get(first, second):
        return Friendship.query.filter(
            or_(
                and_(Friendship.sender_id=first.id,
                     Friendship.receiver_id=second.id),
                and_(Friendship.sender_id=second.id,
                     Friendship.receiver_id=first.id)
            )
        ).first()

    def set_valid(self, valid):
        self.valid = valid
        db.session.add(self)
        db.session.commit()
