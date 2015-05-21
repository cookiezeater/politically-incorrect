import requests
from common import app, db
from random import choice
from sqlalchemy import (
    UniqueConstraint,
    or_,
    and_
)
from itsdangerous import (
    SignatureExpired,
    BadSignature,
    TimedJSONWebSignatureSerializer as Serializer
)
