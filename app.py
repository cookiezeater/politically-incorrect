#!/usr/bin/env python
"""
    app
    ~~~~~
    Launch point for the server.
"""

from flask.ext.script import Manager
from flask.ext.migrate import Migrate, MigrateCommand

from routes import *
from common import app, db
from config import Development

app.config.from_object(Development)

migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
