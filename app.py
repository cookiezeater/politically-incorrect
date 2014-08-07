#!/usr/bin/env python
from routes.player import *
from routes.card import *
from routes.match import *
from routes.game import *
from common import app, db
from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand


__author__ = "Charles S."
__repository__ = "https://github.com/25cf/friends-against-humanity"
__status__ = "Development"


migrate = Migrate(app, db)

manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == "__main__":
    manager.run()
