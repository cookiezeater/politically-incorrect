"""
    test.game
    ~~~~~
    Functional tests
    for game logic.
"""

from test import BaseTest
from models import (
    Card,
    Game,
    Player,
    User
)


class BaseGameTest(BaseTest):
    def setUp(self):
        super(BaseGameTest, self).setUp()
        self.users = {
            'steve': {
                'name'   : 'steve jobs',
                'email'  : 'steve@apple.com',
                'picture': 'steve_jobs.jpg'
            },
            'bill': {
                'name'   : 'bill gates',
                'email'  : 'bill@microsoft.com',
                'picture': 'bill_gates.jpg'
            },
            'mark': {
                'name'   : 'mark zuckerberg',
                'email'  : 'mark@facebook.com',
                'picture': 'mark_zuckerberg.jpg'
            },
            'paul': {
                'name'   : 'paul graham',
                'email'  : 'pg@ycombinator.com',
                'picture': 'pg.jpg'
            },
            'obama': {
                'name'   : 'barack obama',
                'email'  : 'obama@usa.gov',
                'picture': 'obama.jpg'
            }
        }

        for name, user in self.users.items():
            self.users[name]['token'] = User.generate_auth_token(self.users[name]['email'])

        self.db.session.add_all([User(**user) for name, user in self.users.items()])
        self.db.session.commit()


class TestCreateGame(BaseGameTest):
    def test_create_game(self):
        invites = ['obama@usa.gov', 'pg@ycombinator.com', 'mark@facebook.com']
        game    = {
            'name'       : 'first game ever',
            'max_points' : 10,
            'max_players': 5,
            'random'     : True,
            'emails'     : invites
        }
        content, status = self.post_as(self.users['steve']['token'], '/game/create', game)
        self.assertEqual(status, 200)
        self.assertEqual(len(content['players']), len(invites) + 1)
        self.assertIn('id', content)

        id = content['id']

        content, status = self.post_as(self.users['steve']['token'], '/user', {})
        self.assertEqual(content['games'][0]['id'], id)

        content, status = self.post_as(self.users['steve']['token'], '/game/{}'.format(id), {})
        self.assertEqual(len(content['players']), len(invites) + 1)

        obama = next(
            (player for player in content['players'] if player['name'] == 'barack obama'),
            None
        )
        self.assertEqual(obama['status'], 'PENDING')
