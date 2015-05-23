"""
    models.player
    ~~~~~
    Player model and assoc
    tables, which represent
    a user's state inside a game.
"""

from common import db

hands = db.Table(
    'hands',
    db.Model.metadata,
    db.Column('player', db.Integer, db.ForeignKey('players.id')),
    db.Column('card', db.Integer, db.ForeignKey('cards.id'))
)

played = db.Table(
    'played',
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
    | status | score | judged | seen |
    |--------|-------|--------|------|
    | str    | int   | int    | bool |

    relationships
    ~~~~~
    user  : user   <-  player
    game  : game   <-  player
    hand  : player  -  card
    played: player  -  card
    """

    __tablename__ = 'players'

    STATUSES = ('PENDING', 'JOINED')

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='user_to_player'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id', name='game_to_player'), nullable=False)
    status  = db.Column(db.String(7), nullable=False)
    score   = db.Column(db.Integer, nullable=False)
    judged  = db.Column(db.Integer, nullable=False)
    seen    = db.Column(db.Boolean, nullable=False, default=False)
    hand    = db.relationship('Card', secondary=hands)
    played  = db.relationship('Card', secondary=played)

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
        return Player.query.filter_by(user=user, game=game).first()

    def delete(self):
        """Deletes a player. Typically used when declining to join a game."""
        db.session.delete(self)

    def play_cards(self, cards):
        assert not self.played
        self.played = cards
        [self.hand.remove(card) for card in cards]

    def set_status_joined(self):
        """Change player status to JOINED."""
        self.status = 'JOINED'

    def add_points(self, n):
        """Add n points to the player's score."""
        self.score += n

    def __repr__(self):
        return '<player email={} game={} status={}>'.format(
            self.user.email, self.game.id, self.status
        )
