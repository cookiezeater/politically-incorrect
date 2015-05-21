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
