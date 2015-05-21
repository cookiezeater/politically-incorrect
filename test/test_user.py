import sys
import json
from app import app, db
from nose.tools import with_setup
from unittest import (
    TestCase
)


class TestUser(TestCase):
    def setUp(self):
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_registration(self):
        oauth_token = 'ya29.egEj1mjXGkAtbSnBuRXC7oRJMxaLfs3rQ_y8B-56akWHoP7TdAK3wJbaAG4S0weYWdmz28XbBi46mg'
        response = self.app.post(
            '/user', data=json.dumps({ 'token': oauth_token }), headers={ 'content-type': 'application/json' }
        )
        content  = json.loads(response.data)

        assert content['email'] == 'dolphinsandfriends@gmail.com'
        assert content['token'] != oauth_token