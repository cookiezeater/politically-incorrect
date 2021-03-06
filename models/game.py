"""
    models.game
    ~~~~~
    Game model, containing
    information about
    individual games.
"""

from random import choice
from datetime import datetime

from common import db
from models import Card, Player


class Game(db.Model):
    """
    The game model.

    columns
    ~~~~~
    | name | max_points | max_players | status | random | previous_round |
    |------|------------|-------------|--------|--------|----------------|
    | str  | int        | int         | enum   | bool   | pickle         |

    relationships
    ~~~~~
    host      : user    -> game
    black_card: card    -> game
    judge     : player  -> game
    players   : player <-  game
    used_cards: card   <-> game
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
    end_time       = db.Column(db.DateTime, nullable=True)

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

    @staticmethod
    def find_random(user):
        """
        Finds a valid optimal random game
        for the user. This is very inefficient
        and there is a better way to do this.

        TODO: optimize this
        """

        games = Game.query.filter(
            Game.random == True,  # this is not a mistake
            Game.status == Game.PENDING,
            ~Game.players.any(Player.user_id == user.id)
        ).all()

        try:
            game = max(
                games,
                key=lambda g: len([p for p in g.players if p.status == Player.JOINED])
            )
        except ValueError:
            game = None

        return game

    @staticmethod
    def find_n_random(n, user):
        """Finds the top n optimal random games. TODO: optimize THE SHIT OUT OF THIS"""
        games = Game.query.filter(
            Game.random == True,  # this is not a mistake
            Game.status == Game.PENDING,
            ~Game.players.any(Player.user_id == user.id)
        ).all()

        try:
            games = sorted(
                games,
                key=lambda g: len([p for p in g.players if p.status == Player.JOINED])
            )
        except ValueError:
            games = []

        return games if len(games) < n else games[:n]

    def start(self):
        """Begins the game."""
        self.status = self.ONGOING
        [player.delete() for player in self.players if player.status != Player.JOINED]
        self.players = [player for player in self.players if player.status == Player.JOINED]
        self.new_round(None)

    def end(self):
        """Ends the game."""
        for player in self.players:
            if player.user.num_random > 0:
                player.user.num_random -= 1

        self.status   = Game.ENDED
        self.end_time = datetime.now()

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
                        'name'   : player.user.name,
                        'email'  : player.user.email,
                        'picture': player.user.picture,
                        'cards'  : [
                            {
                                'id'  : card.id,
                                'text': card.text
                            }
                            for card in player.get_played()
                        ]
                    }
                    for player in self.players
                    if player.hand and player != self.judge
                ]
            }

        self.winner = None

        if any(player.score == self.max_points for player in self.players):
            self.end()
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
        self.judge.played = [self.black_card.id]
        self.judge.judged += 1

    def invite_all(self, players):
        """Invites a list of players to this game."""
        self.players += players

    def invite(self, player):
        """Invites a single player to this game."""
        self.players.append(player)

    def get_description(self):
        """Returns the description of the game."""
        if self.status == Game.ONGOING:
            players = sorted(self.players, key=lambda p: p.user.name)
            names   = [player.user.name.split(' ')[0] for player in players]
            count   = len(names)

            return '{}, {}, and {} others...'.format(
                names[0], names[1], count - 2
            )

        elif self.status == Game.PENDING:
            joined = [player for player in self.players
                             if player.status == Player.JOINED]
            names  = [player.user.name.split(' ')[0] for player in joined]
            count  = len(names)

            if count == 1:
                return 'This game is hosted by {}!'.format(names[0])
            elif count == 2:
                return '{} and {} have joined this game!'.format(
                    names[0], names[1]
                )
            elif count == 3:
                return '{}, {}, and {} have joined this game!'.format(
                    names[0], names[1], names[2]
                )

            return '{}, {}, and {} others have joined this game!'.format(
                names[0], names[1], count - 2
            )

        elif self.status == Game.ENDED:
            winner = max(self.players, key=lambda p: p.score)
            name   = winner.user.name.split(' ')[0]

            return '{} won the game with {} points!'.format(
                name, winner.score
            )

        return 'Something went horribly wrong...'

    def __repr__(self):
        return '<game id={} players={}>'.format(
            self.id, [player.user.id for player in self.players]
        )
