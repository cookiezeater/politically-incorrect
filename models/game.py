"""
    models.game
    ~~~~~
    Game model, containing
    information about
    individual games.
"""

from models.shared import *


class Game(Base):
    """


    columns
    ~~~~~

    relationships
    ~~~~~
    """
    STATUSES = ('PENDING', 'ONGOING', 'ENDED')

    host_id        = db.Column(db.Integer, ForeignKey('users.id'), nullable=False)
    host           = relationship('User', uselist=False)
    name           = db.Column(db.String(80), nullable=False)
    max_points     = db.Column(db.Integer, nullable=False)
    max_players    = db.Column(db.Integer, nullable=False)
    status         = db.Column(db.String(7), nullable=False)
    black_card_id  = db.Column(db.Integer, ForeignKey('cards.id'))
    black_card     = relationship('Card', uselist=False)
    judge_id       = db.Column(db.Integer, ForeignKey('players.id'))
    judge          = relationship('Player', uselist=False)
    players        = relationship('Player', back_populates('game'))
    previous_round = db.PickleType()
    used_cards     = relationship('Card')

    @staticmethod
    def create(host, name, max_points, max_players, status='PENDING'):
        """Create an uninitialized (pending) match."""
        game = Game(
            host_id=host.id,
            name=name,
            max_points=max_points,
            max_players=max_players,
            status=status
        )
        db.session.add(game)
        return game

    @staticmethod
    def get(id):
        """Get a game by id."""
        return Game.query.get(id)

    def start(self):
        # TODO
        pass

    def new_round(self):
        """Start a new round."""
        if any(player.points == self.max_points for player in self.players):
            self.status = 'ENDED'
            return jsonify()

        self.used_cards.append(black_card)

        black_cards     = Card.get_all(black=True)
        self.black_card = choice(black_cards)

        while self.black_card in set(self.used_cards):
            self.black_card = choice(black_cards)

        self.judge = min(players, key=lambda player: player.judged)
        self.judge.judged += 1

    def invite(self, player):
        self.players.append(player)

    def invite_all(self, players):
        self.players += players

    def __repr__(self):
        return '<game id={} players={}>'.format(
            self.id, [player.user.id for player in self.players]
        )
