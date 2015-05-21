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

    host_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name           = db.Column(db.String(80), nullable=False)
    max_points     = db.Column(db.Integer, nullable=False)
    max_players    = db.Column(db.Integer, nullable=False)
    status         = db.Column(db.String(7), nullable=False)
    black_card_id  = db.Column(db.Integer, db.ForeignKey('cards.id'))
    black_card     = db.relationship('Card')
    judge_id       = db.Column(db.Integer, db.ForeignKey('players.id'))
    judge          = db.relationship('Player', foreign_keys='Game.judge_id')
    players        = db.relationship('Player', backref='game', foreign_keys='Player.game_id')
    previous_round = db.PickleType()
    used_cards     = db.relationship('Card')

    @staticmethod
    def create(host, name, max_points, max_players, status='PENDING'):
        """Create an uninitialized (pending) match."""
        game = Game(
            host=host,
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
        """Begins the game."""
        self.status = 'ONGOING'
        self.new_round(None)

    def new_round(self, winner):
        """
        Starts a new round.

        - Store previous round as Pickled dictionary
        - Fill every player's hand
        - Discard and play a new black card
        - Find a new judge and increment
          his judge count
        """

        if winner:
            self.previous_round = {
                'judge'     : {
                    'name' : self.judge.user.name,
                    'email': self.judge.user.email
                },
                'winner'    : {
                    'name' : winner.user.name,
                    'email': winner.user.email
                },
                'black_card': {
                    'text'   : self.black_card.text,
                    'answers': self.black_card.answers
                },
                'table'     : [
                    {
                        'email': player.user.email,
                        'text' : player.card.text
                    }
                    for player in self.players
                    if player.card and player.card.answers == 0
                ]
            }

        self.winner = None

        if any(player.points == self.max_points for player in self.players):
            self.status = 'ENDED'
            return jsonify()

        white_cards = Card.get_all(black=false)

        # fill every player's hand
        for player in self.players:
            while len(player.hand) < 10:
                white_card = choice(white_cards)

                while white_card in set(self.used_cards):
                    white_card = choice(white_cards)

                player.hand.append(white_card)
                self.used_cards.append(white_card)

        # play a new black card and choose a new judge
        black_cards     = Card.get_all(black=True)
        self.black_card = choice(black_cards)

        while self.black_card in set(self.used_cards):
            self.black_card = choice(black_cards)

        self.used_cards.append(black_card)

        self.judge = min(players, key=lambda player: player.judged)
        self.judge.card = black_card
        self.judge.judged += 1

    def invite_all(self, players):
        """Invites a list of players to this game."""
        self.players += players

    def __repr__(self):
        return '<game id={} players={}>'.format(
            self.id, [player.user.id for player in self.players]
        )
