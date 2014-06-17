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


class Player(Base):
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
    
    def __init__(self, username=None, email=None):
        self.username = username
        self.email = email

    def __str__(self):
        return "Player {}: {}".format(self.username, self.email)


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


class Table(Base):
    __tablename__ = 'tables'

    id = Column(Integer, primary_key=True)
    deck = relationship("Card",
                secondary=association_table) # Many-to-many relationship
    black = relationship("Card", backref="tables") # Many-to-one relationship


class State(Base):
    __tablename__ = 'states'
    
    id = Column(Integer, primary_key=True)
    player = relationship("Player", backref="states") # Many-to-one relationship
    match = relationship("Match",
                    uselist=False, backref="states") # One-to-one relationship
    score = Column(Integer)
    hand = relationship("Card",
                    secondary=association_table)
    played = relationship("Card", backref="states") # Many-to-one relationship
    judged = Column(Integer)
