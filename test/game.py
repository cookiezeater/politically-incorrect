#!/usr/bin/env python

# hack to allow app imports to work in a non-package
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import app
import json
import unittest

headers = {"Content-type": "application/json",
           "Accept": "text/plain"}

default_player = {"player_type": "default",
                  "username": "dostoevsky",
                  "password": "pass",
                  "email": "dostoevsky@gmail.com",
                  "first_name": "fyodor",
                  "last_name": "dostoevsky"}


class GameTestCase(unittest.TestCase):
    def setUp(self):
        self.auth = {}
        self.app = app.app.test_client()
        self.db = app.db
        self.db.drop_all()
        self.db.create_all()
        self.db.session.commit()
        app.app.config["TESTING"] = True

    def tearDown(self):
        self.db.drop_all()
        self.db.session.commit()

    def test_register_default(self):
        response = self.app.post("/players",
                                 data=json.dumps(default_player),
                                 headers=headers)
        data = json.loads(response.data)
        assert response.status == "200 OK", response.status
        assert data["status"] == "success", response.data
        self.auth[default_player["email"]] = data["token"]

    def test_register_google(self):
        pass

    def test_update_google(self):
        pass

    def test_login(self):
        response = self.app.get("/players/login")
        assert response.status == "418 I'M A TEAPOT", response.status
        # todo: valid login


if __name__ == "__main__":
    unittest.main()
