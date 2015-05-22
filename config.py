"""
    config
    ~~~~~
    Contains configuration classes
    for app initialization. Used
    in common.py.
"""

class Base(object):
    SECRET_KEY = '123456789lol'


class Production(Base):
    DATABASE = ''
    USERNAME = ''
    PASSWORD = ''


class Development(Base):
    DEBUG    = True
    DATABASE = 'politically-incorrect-db'
    USERNAME = 'Charles'
    SQLALCHEMY_DATABASE_URI = 'postgres://localhost/politically-incorrect-db'

    PROPAGATE_EXCEPTIONS        = True
    JSONIFY_PRETTYPRINT_REGULAR = True


class Testing(Development):
    TESTING = True
