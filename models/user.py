"""
    models.user
    ~~~~~
    User and Friendship
    models. Encapsulates
    and abstracts access and
    modification functions
    of the User store.
"""

from models.shared import *

TOKEN_EXPIRATION = 696969696969
GOOGLE_URL = \
        "https://www.googleapis.com/oauth2/v1/userinfo?access_token={}"


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
    friends: user <-> user (through Friendship table)
    players: user <-  player
    """

    name    = db.Column(db.String(128), nullable=False)
    email   = db.Column(db.String(128), nullable=False, unique=True)
    picture = db.Column(db.String(255), nullable=False)
    token   = db.Column(db.String(255), nullable=False)
    players = db.relationship('Player', backref='user')
    hosting = db.relationship('Game', backref='host')

    @staticmethod
    def create(oauth_token):
        """Create and return a new user."""
        response = requests.get(GOOGLE_URL.format(oauth_token))
        content  = response.json()
        name     = content['given_name'] + ' ' + content['family_name']
        email    = content['email']
        picture  = content['picture']
        user     = User(
            name=name, email=email, picture=picture, token=User.generate_auth_token(email)
        )
        db.session.add(user)
        return user

    @staticmethod
    def get(email):
        """Get an existing user by email."""
        return User.query.filter(email=email).first()

    @staticmethod
    def get_all(emails):
        """Get a bunch of users by email."""
        or_query = [User.email == email for email in emails]
        return User.query.filter(or_(*or_query)).all()

    @staticmethod
    def auth(token):
        """Authorize and return an existing user."""
        cereal = Serializer(app.config['SECRET_KEY'])
        try:
            data = cereal.loads(token)
        except SignatureExpired:
            # valid but expired token
            return None
        except BadSignature:
            # invalid token
            return None
        except Exception:
            return None
        if 'email' not in data or data['email'] is None:
            return None
        user = User.query.filter(email=data['email']).first()
        return user

    @staticmethod
    def generate_auth_token(email, expiration=TOKEN_EXPIRATION):
        """Generate an auth token from a user's email."""
        cereal = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return cereal.dumps({ 'email': email })

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

    def get_friends(self):
        """Returns the valid friends of the user."""
        friendships = Friendship.get_all_valid(self)
        friends     = []

        for friendship in friendships:
            if friendship.sender != self:
                friends.append(friendship.sender)
            else:
                friends.append(friendship.receiver)

        return friends

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
        return "<user {}>".format(self.email)


class Friendship(Base):
    """A simple table of one-to-one friendships."""
    sender_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    sender      = db.relationship('User', uselist=False, foreign_keys='Friendship.sender_id')
    receiver    = db.relationship('User', uselist=False, foreign_keys='Friendship.receiver_id')
    valid       = db.Column(db.Boolean, nullable=False, default=False)

    __table_args__ = (UniqueConstraint('sender_id', 'receiver_id'),)

    @staticmethod
    def create(sender, receiver):
        """Create an invalid friendship entry."""
        assert not Friendship.get(sender, receiver)
        friendship = Friendship(sender=sender, receiver=receiver, valid=False)
        db.session.add(friendship)
        return friendship

    @staticmethod
    def get(first, second):
        """Get the existing friendship entry, regardless of validity."""
        return Friendship.query.filter(
            or_(
                and_(
                    Friendship.sender == first,
                    Friendship.receiver == second
                ),
                and_(
                    Friendship.sender == second,
                    Friendship.receiver == first
                )
            )
        ).first()

    @staticmethod
    def get_all_valid(user):
        """Get all of a user's valid friendships."""
        return Friendship.query.filter(
            Friendship.valid == True,
            or_(
                Friendship.sender == user,
                Friendship.receiver == user
            )
        ).all()

    def set_valid(self, valid):
        """Change the validity of a friendship."""
        self.valid = valid

    def __repr__(self):
        return '<friendship sender={} receiver={} valid={}>'.format(
            self.sender.email, self.receiver.email, self.valid
        )
