"""
    models.player
    ~~~~~
    Player model, which represents
    a user's state inside a game.
"""

from models.shared import *


class Player(Base):
    """
    Player model containing
    functions which encapsulate
    gameplay state changes.

    columns
    ~~~~~
    | status | score | judged |
    |--------|-------|--------|
    | str    | int   | int

    relationships
    ~~~~~
    user  : user   <-  player
    game  : game   <-  player
    hand  : player  -  card
    played: player  -  card
    """

    STATUSES = ('PENDING', 'JOINED')

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"), nullable=False)
    user    = relationship('User', uselist=False, back_populates='players')
    game    = relationship('Game', uselist=False, back_populates='players')
    status  = db.Column(db.String(10), nullable=False)
    score   = db.Column(db.Integer, nullable=False)
    judged  = db.Column(db.Integer, nullable=False)
    hand    = relationship('Card')
    played  = relationship('Card')

    @staticmethod
    def create(user, game):
        """Creates a single uninitialized player."""
        player = Player(
            user_id=user.id, game_id=game.id, status='PENDING', score=0, judged=0
        )
        db.session.add(player)
        return player

    @staticmethod
    def create_all(users, game):
        """Creates many players for a given game."""
        players = [
            Player(
                user_id=user.id, game_id=game.id, status='PENDING', score=0, judged=0
            )
            for user in users
        ]
        db.session.add_all(players)
        return players

    @staticmethod
    def get(user, game):
        """Returns the player associated with a specific user and game."""
        return Player.query.filter(user_id=user.id, game_id=game.id).first()

    def delete(self):
        """Deletes a player. Typically used when declining to join a game."""
        # TODO
        pass

    def set_status_joined(self):
        """Change player status to JOINED."""
        self.status = 'JOINED'
        db.session.add(self)
