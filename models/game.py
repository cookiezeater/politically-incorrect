"""
    models.game
    ~~~~~
    Game model, containing
    information about
    individual games.
"""

from random import choice

from common import db
from models import Card, Player


class Game(db.Model):
    """


    columns
    ~~~~~

    relationships
    ~~~~~
    """

    __tablename__ = 'games'

    ONGOING = 0
    PENDING = 1
    ENDED   = 2

    id             = db.Column(db.Integer, primary_key=True)
    host_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name           = db.Column(db.String(80), nullable=False)
    max_points     = db.Column(db.Integer, nullable=False)
    max_players    = db.Column(db.Integer, nullable=False)
    status         = db.Column(db.Integer, nullable=False)
    random         = db.Column(db.Boolean, nullable=False)
    black_card_id  = db.Column(db.Integer, db.ForeignKey('cards.id'))
    black_card     = db.relationship('Card')
    judge_id       = db.Column(db.Integer, db.ForeignKey('players.id'))
    judge          = db.relationship('Player', foreign_keys='Game.judge_id', post_update=True)
    players        = db.relationship('Player', backref='game', foreign_keys='Player.game_id')
    previous_round = db.Column(db.PickleType)
    used_cards     = db.relationship('Card', uselist=True)

    @staticmethod
    def create(host, name, max_points, max_players, random):
        """Create an uninitialized (pending) match."""
        game = Game(
            host_id=host.id,
            name=name,
            max_points=max_points,
            max_players=max_players,
            random=random,
            status=Game.PENDING,
            previous_round={},
            used_cards=[]
        )
        db.session.add(game)
        return game

    @staticmethod
    def get(id):
        """Get a game by id."""
        return Game.query.get(id)

    def start(self):
        """Begins the game."""
        self.status = self.ONGOING
        [player.delete() for player in self.players if player.status != Player.JOINED]
        self.players = [player for player in self.players if player.status == Player.JOINED]
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
                    'id'     : self.black_card.id,
                    'text'   : self.black_card.text,
                    'answers': self.black_card.answers
                },
                'table'     : [
                    {
                        'email' : player.user.email,
                        'played': [
                            {
                                'id'  : card.id,
                                'text': card.text
                            }
                            for card in player.played
                        ]
                    }
                    for player in self.players
                    if player.hand and all(card.answers == 0 for card in player.hand)
                ]
            }

        self.winner = None

        if any(player.score == self.max_points for player in self.players):
            self.status = Game.ENDED
            return

        white_cards = Card.get_all(black=False)

        # fill every player's hand and remove their played card
        for player in self.players:
            player.played = []

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

        self.used_cards.append(self.black_card)

        self.judge = min(self.players, key=lambda player: player.judged)
        self.judge.played = [self.black_card]
        self.judge.judged += 1

    def invite_all(self, players):
        """Invites a list of players to this game."""
        self.players += players

    def get_description(self):
        others = sorted(self.players, key=lambda p: p.user.name)
        names  = [player.user.name.split(' ')[0] for player in others]
        count  = len(self.players)

        if count == 1:
            return 'You\'re the only one in this game.'
        elif count <= 3:
            return 'There are {} people in this game.'.format(count)

        return '{}, {}, and {} others...'.format(
            names[0], names[1], count - 2
        )

    def __repr__(self):
        return '<game id={} players={}>'.format(
            self.id, [player.user.id for player in self.players]
        )
