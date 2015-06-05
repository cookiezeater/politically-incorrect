"""
    models.player
    ~~~~~
    Player model and assoc
    tables, which represent
    a user's state inside a game.
"""

from sqlalchemy import or_

from common import db
from models import Card

hands = db.Table(
    'hands',
    db.Model.metadata,
    db.Column('player', db.Integer, db.ForeignKey('players.id')),
    db.Column('card', db.Integer, db.ForeignKey('cards.id'))
)


class Player(db.Model):
    """
    Player model containing
    functions which encapsulate
    gameplay state changes.

    columns
    ~~~~~
    | status | score | judged | seen | played |
    |--------|-------|--------|------|--------|
    | enum   | int   | int    | bool | pickle |

    relationships
    ~~~~~
    user  : user   <-  player
    game  : game   <-  player
    hand  : player  -  card
    """

    __tablename__ = 'players'

    PENDING  = 0
    JOINED   = 1
    REJECTED = 2

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='user_to_player'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', name='game_to_player'), nullable=False)
    status  = db.Column(db.Integer, nullable=False)
    score   = db.Column(db.Integer, nullable=False)
    judged  = db.Column(db.Integer, nullable=False)
    seen    = db.Column(db.Boolean, nullable=False, default=False)
    played  = db.Column(db.PickleType, nullable=True)
    hand    = db.relationship('Card', secondary=hands)

    @staticmethod
    def create(user, game):
        """Creates a single uninitialized player."""
        player = Player(
            user=user, game=game, status=Player.PENDING, score=0, judged=0
        )
        db.session.add(player)
        return player

    @staticmethod
    def create_all(users, game):
        """Creates many players for a given game."""
        players = [
            Player(
                user=user, game=game, status=Player.PENDING, score=0, judged=0
            )
            for user in users
        ]
        db.session.add_all(players)
        return players

    @staticmethod
    def get(user, game):
        """Returns the player associated with a specific user and game."""
        return Player.query.filter_by(user=user, game=game).first()

    def delete(self):
        """Deletes a player. Typically used when declining to join a game."""
        db.session.delete(self)

    def get_played(self):
        """
        Store the player's played cards as a list of
        card ids. This is necessary for efficiently
        enforcing played order. The nested loop below
        is still faster than making one query for each card.
        """

        if not self.played:
            return []

        cards  = Card.query.filter(
            or_(Card.id == card_id for card_id in self.played)
        ).all()
        played = []

        for card_id in self.played:
            card = next(
                (c for c in cards if c.id == card_id),
                None
            )
            played.append(card)

        return played

    def play_cards(self, cards):
        assert not self.played
        self.played = [card.id for card in cards]
        [self.hand.remove(card) for card in cards]

    def set_status_joined(self):
        """Change player status to JOINED."""
        self.status = Player.JOINED

    def set_status_denied(self):
        """Change player status to DENIED."""
        self.status = Player.DENIED

    def add_points(self, n):
        """Add n points to the player's score."""
        self.score += n

    def __repr__(self):
        return '<player email={} game={} status={}>'.format(
            self.user.email, self.game.id, self.status
        )
