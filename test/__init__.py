"""
    test.__init__
    ~~~~~
    Not meant for importing
    outside of the test
    package. Contains shared
    classes and functions for
    tests.
"""

import json
from common import app, db
from config import Testing
from unittest import TestCase


class BaseTest(TestCase):
    def setUp(self):
        self.db    = db
        self.app   = app.test_client()
        self.oauth = 'ya29.ewFrfj5PwQ37RHbvK971NdfvLWHPCbBdQWytY8iAoAaEeYpouuhksd4IO-gvtz6IbiQx3yqlvK27Dg'

        app.config.from_object(Testing)
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def post(self, url, data):
        data     = json.dumps(data)
        headers  = { 'content-type': 'application/json' }
        response = self.app.post(url, data=data, headers=headers)
        content  = json.loads(response.data)
        return content, response.status_code

    def post_as(self, token, url, data):
        data['token'] = token
        data          = json.dumps(data)
        headers       = { 'content-type': 'application/json' }
        response      = self.app.post(url, data=data, headers=headers)
        content       = json.loads(response.data)
        return content, response.status_code
