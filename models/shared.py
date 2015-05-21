import requests
from common import app, db
from random import choice
from sqlalchemy import (
    UniqueConstraint,
    or_,
    and_
)
from sqlalchemy.ext.declarative import (
    declarative_base,
    as_declarative,
    declared_attr
)
from itsdangerous import (
    SignatureExpired,
    BadSignature,
    TimedJSONWebSignatureSerializer as Serializer
)


@as_declarative()
class Base(object):
    """
    Base model. Default columns
    are a primary key id, created_on,
    and updated_on columns. Default
    tablename is set to plural lowercase
    of the model name.
    """

    id         = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    query = db.session.query_property()

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'


Base = declarative_base(cls=Base)
