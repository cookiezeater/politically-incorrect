"""
    models.player
    ~~~~~
    Player model and assoc
    tables, which represent
    a user's state inside a game.
"""

from models.shared import *


hands = db.Table(
    'hands',
    Base.metadata,
    db.Column('player', db.Integer, db.ForeignKey('players.id')),
    db.Column('card', db.Integer, db.ForeignKey('cards.id'))
)


class Player(Base):
    """
    Player model containing
    functions which encapsulate
    gameplay state changes.

    columns
    ~~~~~
    | status | score | judged |
    |--------|-------|--------|
    | str    | int   | int    |

    relationships
    ~~~~~
    user  : user   <-  player
    game  : game   <-  player
    hand  : player  -  card
    played: player  -  card
    """

    STATUSES = ('PENDING', 'JOINED')

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    status  = db.Column(db.String(7), nullable=False)
    score   = db.Column(db.Integer, nullable=False)
    judged  = db.Column(db.Integer, nullable=False)
    hand    = db.relationship('Card', secondary=hands)

    @staticmethod
    def create(user, game):
        """Creates a single uninitialized player."""
        player = Player(
            user=user, game=game, status='PENDING', score=0, judged=0
        )
        db.session.add(player)
        return player

    @staticmethod
    def create_all(users, game):
        """Creates many players for a given game."""
        players = [
            Player(
                user=user, game=game, status='PENDING', score=0, judged=0
            )
            for user in users
        ]
        db.session.add_all(players)
        return players

    @staticmethod
    def get(user, game):
        """Returns the player associated with a specific user and game."""
        return Player.query.filter(user=user, game=game).first()

    def delete(self):
        """Deletes a player. Typically used when declining to join a game."""
        # TODO
        pass

    def play_card(self, card):
        assert not self.card
        self.card = card
        self.hand.remove(card)

    def set_status_joined(self):
        """Change player status to JOINED."""
        self.status = 'JOINED'

    def add_points(n):
        """Add n points to the player's score."""
        self.points += n
