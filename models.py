"""
@todo:
    - __init__ for most classes
    - __str__ for most classes
    - helper functs for most classes
    - docs
"""

from app import db

players_to_matches = db.Table('p2m', db.Model.metadata,
    db.Column('players_id', db.Integer, db.ForeignKey('players.id')),
    db.Column('matches_id', db.Integer, db.ForeignKey('matches.id')))

players_to_players = db.Table('p2p', db.Model.metadata,
    db.Column('players_id', db.Integer, db.ForeignKey('players.id')),
    db.Column('players_id', db.Integer, db.ForeignKey('players.id')))

states_to_cards = db.Table('s2c', db.Model.metadata,
    db.Column('states_id', db.Integer, db.ForeignKey('states.id')),
    db.Column('cards_id', db.Integer, db.ForeignKey('cards.id')))

matches_to_players = db.Table('m2p', db.Model.metadata,
    db.Column('matches_id', db.Integer, db.ForeignKey('matches.id')),
    db.Column('players_id', db.Integer, db.ForeignKey('players.id')))

matches_to_cards = db.Table('m2c', db.Model.metadata,
    db.Column('matches_id', db.Integer, db.ForeignKey('matches.id')),
    db.Column('cards_id', db.Integer, db.ForeignKey('cards.id')))

class Card(db.Model):
    """
    Represents a player-made card. Scaffold should contain
    default Cards Against Humanity cards for testing purposes.
    """

    __tablename__ = 'cards'
    id = db.Column(db.Integer, primary_key=True)

    text = db.Column(db.String(120), unique=True)
    white = db.Column(db.Boolean)
    rank = db.Column(db.Integer)
    meta = db.Column(db.String(500))

    # One-to-many:
    # A match has one black card at any time,
    # but a black card can be in many matches.
    matches = db.relationship('Match', backref='cards')

    def __init__(self, text=None, white=True):
        self.text = text
        self.white = white

    def __str__(self):
        return "{} Card: {}".format("White" if self.white else "Black",
                                    self.text)

class Player(db.Model):
    """
    Represents a player.
    """

    __tablename__ = 'players'
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(120), unique=True)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    losses = db.Column(db.Integer)

    # One-to-many:
    # A match only has one winner, but a winner can have many won matches.
    wins = db.relationship('Match', backref='winner')

    # Many-to-many:
    # A player has many friends,
    # and any friend can have many friends
    friends = db.relationship("Player", secondary=players_to_players)

    # Many-to-many:
    # A player can be in many matches,
    # and matches have many players
    matches = db.relationship("Match", secondary=players_to_matches,
                                backref="players")

    # One-to-many:
    # A player has many states, but a state can only have one player.
    states = db.relationship('State', backref='player')

    def __init__(self,
                username=None,
                email=None,
                first_name="",
                last_name=""):
        self.username = username
        self.email = email
        self.first_name = first_name
        self.last_name = last_name

        self.matches = None
        self.friends = None
        self.wins = 0
        self.losses = 0

    def __str__(self):
        return "Player {}: {}".format(self.username, self.email)

class Match(db.Model):
    """
    @todo:
        - add table-level enforcement of status choices
    """

    STATUSES = "PENDING", "ONGOING", "ENDED"

    __tablename__ = 'matches'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(7))

    # One-to-many:
    # A match has many states, but a state can only have one match.
    states = db.relationship('State', backref='match')

    # Many-to-many:
    # A match can have many pending players,
    # and a pending player can have many pending matches.
    pending = db.relationship("Player", secondary=matches_to_players)

    # Many-to-one:
    # A match only has one winner, but a winner can have many won matches.
    winner_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    # Many-to-many:
    # A match has many cards in a deck,
    # and cards can have many decks in many matches.
    deck = db.relationship("Card", secondary=matches_to_cards)

    # Many-to-one:
    # A match has one black card at any time,
    # but a black card can be in many matches.
    black_id = db.Column(db.Integer, db.ForeignKey('cards.id'))

    def __init__(self,
                host=None,
                status="PENDING",
                state=None,
                pending=[],
                table=None,
                winner_id=-1,
                winner=None):
        raise NotImplementedError

    def __str__(self):
        players = "get_all_players"
        raise NotImplementedError
        return "Match players: {}, status: {}, judge: {}".format(
                    players, self.status, self.judge)

class State(db.Model):
    __tablename__ = 'states'
    id = db.Column(db.Integer, primary_key=True)

    score = db.Column(db.Integer)
    judged = db.Column(db.Integer)

    # Many-to-one:
    # A state has one player, but a player can have many states.
    player_id = db.Column(db.Integer, db.ForeignKey('players.id'))

    # Many-to-one:
    # A state has one match, but a match has many states.
    match_id = db.Column(db.Integer, db.ForeignKey('matches.id'))

    # Many-to-many:
    # A state has a hand with many cards,
    # and cards can belong to many hands in many states.
    hand = db.relationship("Card", secondary=states_to_cards)

    # Many-to-one:
    # A state has one played card,
    # but a card can have many states in which it is played.
    played_id = db.Column(db.Integer, db.ForeignKey('cards.id'))

    def __init__(self, player=None, match=None, score=0,
                    hand=[], played=None, judged=0):
        raise NotImplementedError

    def __str__(self):
        return "State: Player {}, Match {}".format(self.player, self.match)
