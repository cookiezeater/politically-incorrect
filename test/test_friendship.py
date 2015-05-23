"""
    test.test_friendship
    ~~~~~
    Tests friendship logic.
"""

from test import BaseTest
from models import User, Friendship

PENDING = 'PENDING'
REQUEST = 'REQUEST'
VALID   = 'VALID'


class BaseFriendshipTest(BaseTest):
    def setUp(self):
        super(BaseFriendshipTest, self).setUp()
        self.steve = {
            'name'   : 'steve jobs',
            'email'  : 'steve@apple.com',
            'picture': 'steve_jobs.jpg',
            'token'  : User.generate_auth_token('steve@apple.com')
        }
        self.bill = {
            'name'   : 'bill gates',
            'email'  : 'bill@microsoft.com',
            'picture': 'bill_gates.jpg',
            'token'  : User.generate_auth_token('bill@microsoft.com')
        }
        self.db.session.add_all([User(**self.steve), User(**self.bill)])
        self.db.session.commit()


class TestFriendshipRequest(BaseFriendshipTest):
    def test_add_friend(self):
        content, status = self.post_as(
            self.steve['token'], '/user/friend/add', { 'email': self.bill['email'] }
        )
        self.assertEqual(status, 200)

        content, status = self.post_as(self.steve['token'], '/user', {})
        self.assertEqual(status, 200)
        self.assertEqual(content['friends'][0]['email'], self.bill['email'])
        self.assertEqual(content['friends'][0]['status'], PENDING)

        content, status = self.post_as(self.bill['token'], '/user', {})
        self.assertEqual(status, 200)
        self.assertEqual(content['friends'][0]['email'], self.steve['email'])
        self.assertEqual(content['friends'][0]['status'], REQUEST)


class TestFriendshipAcceptReject(BaseFriendshipTest):
    def setUp(self):
        super(TestFriendshipAcceptReject, self).setUp()
        users      = User.query.all()
        friendship = Friendship(sender=users[0], receiver=users[1])
        self.db.session.add(friendship)
        self.db.session.commit()

    def test_accept_friend(self):
        content, status = self.post_as(
            self.bill['token'], '/user/friend/add', { 'email': self.steve['email'] }
        )

        content, status = self.post_as(self.steve['token'], '/user', {})
        self.assertEqual(status, 200)
        self.assertEqual(content['friends'][0]['email'], self.bill['email'])
        self.assertEqual(content['friends'][0]['status'], VALID)

        content, status = self.post_as(self.bill['token'], '/user', {})
        self.assertEqual(status, 200)
        self.assertEqual(content['friends'][0]['email'], self.steve['email'])
        self.assertEqual(content['friends'][0]['status'], VALID)

    def test_reject_friend(self):
        content, status = self.post_as(
            self.bill['token'], '/user/friend/delete', { 'email': self.steve['email'] }
        )

        content, status = self.post_as(self.steve['token'], '/user', {})
        self.assertEqual(status, 200)
        self.assertEqual(len(content['friends']), 0)

        content, status = self.post_as(self.bill['token'], '/user', {})
        self.assertEqual(status, 200)
        self.assertEqual(len(content['friends']), 0)