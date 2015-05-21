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
        oauth_token = 'ya29.egGrW9rJIMs35sIPewfVbOTlFI0nurl1CbP-6PdachIN_YXKrEZrEPeRW5CgSNkLlIVf58-MgxEazw'
        response = self.app.post(
            '/user', data=json.dumps({ 'token': oauth_token }), headers={ 'content-type': 'application/json' }
        )
        content  = json.loads(response.data)

        assert content['email'] == 'dolphinsandfriends@gmail.com'
        assert content['token'] != oauth_token
