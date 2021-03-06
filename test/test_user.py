"""
    test.user
    ~~~~~
    Tests user routes,
    including oauth
    registration and login.
"""

from test import BaseTest
from models import User


class TestRegistration(BaseTest):
    def test_registration(self):
        content, status = self.post('/user', { 'token': self.oauth, 'device': 'bla' })

        self.assertEqual(status, 200)
        self.assertEqual(content['email'], 'dolphinsandfriends@gmail.com')
        self.assertNotEqual(content['token'], self.oauth)

    def test_invalid_registration(self):
        content, status = self.post('/user', { 'token': 'lol', 'device': 'lol' })

        self.assertNotEqual(status, 200)


class TestLogin(BaseTest):
    def setUp(self):
        super(TestLogin, self).setUp()
        self.user = User.create(self.oauth)
        self.db.session.commit()

    def test_existing_oauth_login(self):
        content, status = self.post('/user', { 'token': self.oauth, 'device': 'new device!' })

        self.assertEqual(status, 200)
        self.assertEqual(content['email'], 'dolphinsandfriends@gmail.com')
        self.assertNotEqual(content['token'], self.oauth)

    def test_existing_token_login(self):
        content, status = self.post('/user', { 'token': self.oauth, 'device': 'new device2' })

        self.assertEqual(status, 200)
        self.assertEqual(content['email'], 'dolphinsandfriends@gmail.com')
        self.assertNotEqual(content['token'], self.oauth)

        token = content['token']
        content, status = self.post_as(token, '/user', {})

        self.assertEqual(status, 200)
        self.assertEqual(content['email'], 'dolphinsandfriends@gmail.com')
        self.assertEqual(content['token'], token)
