from common import app, db
from sqlalchemy.ext.declarative import declarative_base
from itsdangerous import (
    SignatureExpired,
    BadSignature,
    TimedJSONWebSignatureSerializer as Serializer
)


class Base(object):
    """
    Base model. Default columns
    are a primary key id, created_on,
    and updated_on columns. Default
    tablename is set to plural lowercase
    of the model name.
    """

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower() + 's'

    id = db.Column(db.Integer, primary_key=True)
    created_on = db.Column(db.DateTime, default=db.func.now())
    updated_on = db.Column(
        db.DateTime,
        default=db.func.now(),
        onupdate=db.func.now()
    )


Base = declarative_base(cls=Base)
