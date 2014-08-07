#!/usr/bin/env python
from routes.player import *
from routes.card import *
from routes.match import *
from routes.game import *
from common import app, db


__author__ = "Charles S."
__repository__ = "https://github.com/25cf/friends-against-humanity"
__status__ = "Development"


if __name__ == "__main__":
    db.create_all()
    app.run()

