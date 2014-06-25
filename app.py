#!/usr/bin/env python
from routes.player import *
from routes.card import *
from routes.match import *
from common import app, db

if __name__ == "__main__":
    db.create_all()
    app.run()
