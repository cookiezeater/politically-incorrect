#!/usr/bin/env python

# hack to allow app imports to work in a non-package
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import app
import unittest


class PlayerTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        self.db = app.db
        self.db.destroy_all()
        self.db.create_all()
        self.db.session.commit()
        app.app.config["TESTING"] = True

    def tearDown(self):
        self.db.destroy_all()
        self.db.session.commit()

if __name__ == "__main__":
    unittest.main()
