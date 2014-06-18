"""
@todo:
    - __init__ for most classes
    - __str__ for most classes
    - helper functs for most classes
    - docs
"""

from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

association_table = Table('association', Base.metadata,
    Column('left_id', Integer, ForeignKey('left.id')),
    Column('right_id', Integer, ForeignKey('right.id'))
)

class Card(Base):
    """
    Represents a player-made card. Scaffold should contain
    default Cards Against Humanity cards for testing purposes.
    """

    __tablename__ = 'cards'

    id = Column(Integer, primary_key=True)
    text = Column(String(120), unique=True)
    rank = Column(Integer)
    white = Column(Boolean)
    meta = Column(String(500))

    def __init__(self, text=None, rank=0, white=True, meta=""):
        self.text = text
        self.rank = rank
        self.white = white
        self.meta = meta

    def __str__(self):
        return "{} Card: {}".format("White" if white else "Black", self.text)

    def white(self):
        raise NotImplementedError


class Player(Base):
    """
    Represents a player.
    """

    __tablename__ = 'players'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True)
    email = Column(String(120), unique=True)
    first_name = Column(String(50))
    last_name = Column(String(50))
    matches = relationship("Match",
                    secondary=association_table) # Many-to-many relationship
    friends = relationship("Player",
                    secondary=association_table) # Many-to-many relationship
    wins = Column(Integer)
    losses = Column(Integer)

    def __init__(self, username=None, email=None,
                    first_name="", last_name=""):
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

    def friends(self):
        raise NotImplementedError

    def ended_matches(self):
        raise NotImplementedError

    def ongoing_matches(self):
        raise NotImplementedError

    def all_matches(self):
        raise NotImplementedError


class Match(Base):
    """
    @todo:
        - add table-level enforcement of status choices
    """

    STATUSES = "PENDING", "ONGOING", "ENDED"

    __tablename__ = 'matches'

    id = Column(Integer, primary_key=True)
    status = Column(String(7))
    state = relationship("State", backref="matches") # One-to-many relationship
    pending = relationship("Player",
                    secondary=association_table) # Many-to-many relationship
    table = relationship("Table",
                    uselist=False, backref="matches") # One-to-one relationship

    # Many-to-one relationship
    winner_id = Column(Integer, ForeignKey('player.id'))
    winner = relationship("Player")

    def __init__(self, host=None, status="PENDING",
                    state=None, pending=[], table=None,
                    winner_id=-1, winner=None):
        raise NotImplementedError

    def __str__(self):
        players = "get_all_players"
        raise NotImplementedError
        return "Match players: {}, status: {}, judge: {}".format(players, self.status, self.judge)

    def status(self):
        raise NotImplementedError


class Table(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True)
    deck = relationship("Card",
                secondary=association_table) # Many-to-many relationship
    black = relationship("Card", backref="tables") # Many-to-one relationship

    def __init__(self, deck=[], black=None):
        raise NotImplementedError

    def __str__(self):
        return "Table"


class State(Base):
    __tablename__ = 'states'

    id = Column(Integer, primary_key=True)
    player = relationship("Player", backref="states") # Many-to-one relationship
    match = relationship("Match",
                    uselist=False, backref="states") # One-to-one relationship
    score = Column(Integer)
    hand = relationship("Card",
                    secondary=association_table) # Many-to-many relationship
    played = relationship("Card", backref="states") # Many-to-one relationship
    judged = Column(Integer)

    def __init__(self, player=None, match=None, score=0,
                    hand=[], played=None, judged=0):
        raise NotImplementedError

    def __str__(self):
        return "State: Player {}, Match {}".format(self.player, self.match)
