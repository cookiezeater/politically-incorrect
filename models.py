"""
@todo:
    - __init__ for most classes
    - __str__ for most classes
    - helper functs for most classes
    - docs
"""

from app import app, db

# association_table = db.Table('association', db.Model.metadata,
#     db.Column('left_id', db.Integer, db.ForeignKey('left.id')),
#     db.Column('right_id', db.Integer, db.ForeignKey('right.id'))
# )

class Card(db.Model):
    """
    Represents a player-made card. Scaffold should contain
    default Cards Against Humanity cards for testing purposes.
    """

    __tablename__ = 'cards'

    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(120), unique=True)
    rank = db.Column(db.Integer)
    white = db.Column(db.Boolean)
    meta = db.Column(db.String(500))

    def __init__(self, text=None, rank=0, white=True, meta=""):
        self.text = text
        self.rank = rank
        self.white = white
        self.meta = meta

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "{} Card: {}".format("White" if self.white else "Black", self.text)

    def white(self):
        raise NotImplementedError


# class Player(db.Model):
#     """
#     Represents a player.
#     """

#     __tablename__ = 'players'

#     id = db.Column(db.Integer, primary_key=True)
#     username = db.Column(db.String(50), unique=True)
#     email = db.Column(db.String(120), unique=True)
#     first_name = db.Column(db.String(50))
#     last_name = db.Column(db.String(50))
#     matches = db.relationship("Match",
#                     secondary=association_table) # Many-to-many db.relationship
#     friends = db.relationship("Player",
#                     secondary=association_table) # Many-to-many db.relationship
#     wins = db.Column(db.Integer)
#     losses = db.Column(db.Integer)

#     def __init__(self, username=None, email=None,
#                     first_name="", last_name=""):
#         self.username = username
#         self.email = email
#         self.first_name = first_name
#         self.last_name = last_name

#         self.matches = None
#         self.friends = None
#         self.wins = 0
#         self.losses = 0

#     def __str__(self):
#         return "Player {}: {}".format(self.username, self.email)

#     def friends(self):
#         raise NotImplementedError

#     def ended_matches(self):
#         raise NotImplementedError

#     def ongoing_matches(self):
#         raise NotImplementedError

#     def all_matches(self):
#         raise NotImplementedError

# class Match(db.Model):
#     """
#     @todo:
#         - add table-level enforcement of status choices
#     """

#     STATUSES = "PENDING", "ONGOING", "ENDED"

#     __tablename__ = 'matches'

#     id = db.Column(db.Integer, primary_key=True)
#     status = db.Column(db.String(7))
#     state = db.relationship("State", db.backref="matches") # One-to-many db.relationship
#     pending = db.relationship("Player",
#                     secondary=association_table) # Many-to-many db.relationship
#     table = db.relationship("db.Table",
#                     uselist=False, db.backref="matches") # One-to-one db.relationship

#     # Many-to-one db.relationship
#     winner_id = db.Column(db.Integer, db.ForeignKey('player.id'))
#     winner = db.relationship("Player")

#     def __init__(self, host=None, status="PENDING",
#                     state=None, pending=[], table=None,
#                     winner_id=-1, winner=None):
#         raise NotImplementedError

#     def __str__(self):
#         players = "get_all_players"
#         raise NotImplementedError
#         return "Match players: {}, status: {}, judge: {}".format(players, self.status, self.judge)

#     def status(self):
#         raise NotImplementedError

# class db.Table(db.Model):
#     __tablename__ = 'tables'

#     id = db.Column(db.Integer, primary_key=True)
#     deck = db.relationship("Card",
#                 secondary=association_table) # Many-to-many db.relationship
#     black = db.relationship("Card", db.backref="tables") # Many-to-one db.relationship

#     def __init__(self, deck=[], black=None):
#         raise NotImplementedError

#     def __str__(self):
#         return "db.Table"

# class State(db.Model):
#     __tablename__ = 'states'

#     id = db.Column(db.Integer, primary_key=True)
#     player = db.relationship("Player", db.backref="states") # Many-to-one db.relationship
#     match = db.relationship("Match",
#                     uselist=False, db.backref="states") # One-to-one db.relationship
#     score = db.Column(db.Integer)
#     hand = db.relationship("Card",
#                     secondary=association_table) # Many-to-many db.relationship
#     played = db.relationship("Card", db.backref="states") # Many-to-one db.relationship
#     judged = db.Column(db.Integer)

#     def __init__(self, player=None, match=None, score=0,
#                     hand=[], played=None, judged=0):
#         raise NotImplementedError

#     def __str__(self):
#         return "State: Player {}, Match {}".format(self.player, self.match)
