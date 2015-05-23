# -*- coding: utf-8 -*- 
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
        self.assertEqual(obama['status'], Player.PENDING)

        content, status = self.post_as(self.users['obama']['token'], '/user', {})
        self.assertEqual(len(content['games']), 1)
        self.assertEqual(content['games'][0]['status'], Game.PENDING)


class TestGameAcceptInvite(BaseGameTest):
    def setUp(self):
        super(TestGameAcceptInvite, self).setUp()
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
        self.game = content

    def test_send_invite(self):
        content, status = self.post_as(
            self.users['steve']['token'], '/game/{}/invite'.format(self.game['id']), { 'emails': ['bill@microsoft.com'] }
        )
        self.assertEqual(status, 200)

        content, status = self.post_as(
            self.users['steve']['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(content['players']), 5)

        player_statuses = [player['status'] for player in content['players']]
        self.assertEqual(player_statuses.count(Player.JOINED), 1)
        self.assertEqual(player_statuses.count(Player.PENDING), len(player_statuses) - 1)

        content, status = self.post_as(self.users['bill']['token'], '/user', {})
        self.assertEqual(status, 200)
        self.assertEqual(len(content['games']), 1)

        content, status = self.post_as(
            self.users['bill']['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(content['name'], self.game['name'])

    def test_accept_invite(self):
        content, status = self.post_as(
            self.users['steve']['token'], '/game/{}/invite'.format(self.game['id']), { 'emails': ['bill@microsoft.com'] }
        )
        self.assertEqual(status, 200)

        content, status = self.post_as(
            self.users['bill']['token'], '/game/{}/add'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(content['started'], False)

        content, status = self.post_as(
            self.users['obama']['token'], '/game/{}/add'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(content['started'], False)

        content, status = self.post_as(
            self.users['steve']['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)

        player_statuses = [player['status'] for player in content['players']]
        self.assertEqual(player_statuses.count(Player.JOINED), 3)
        self.assertEqual(player_statuses.count(Player.PENDING), len(player_statuses) - 3)

        content, status = self.post_as(
            self.users['bill']['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)

        player_statuses = [player['status'] for player in content['players']]
        self.assertEqual(player_statuses.count(Player.JOINED), 3)
        self.assertEqual(player_statuses.count(Player.PENDING), len(player_statuses) - 3)


class TestGameAcceptInvite(BaseGameTest):
    def setUp(self):
        super(TestGameAcceptInvite, self).setUp()

        # load cards
        with open('cards/black.txt') as black, \
             open('cards/white.txt') as white:
            black_text = list(set(black.readlines()))
            white_text = list(set(white.readlines()))

        white_cards = [
            Card(text=text, answers=0) for text in white_text
        ]
        black_cards = [
            Card(text=text, answers=text.count('████')) for text in black_text
        ]
        self.db.session.add_all(white_cards + black_cards)
        self.db.session.commit()

    def test_full_game(self):
        # create initial pending game
        invites = ['obama@usa.gov', 'pg@ycombinator.com', 'mark@facebook.com']
        game    = {
            'name'       : 'first game ever',
            'max_points' : 2,
            'max_players': 3,
            'random'     : True,
            'emails'     : invites
        }
        content, status = self.post_as(self.users['steve']['token'], '/game/create', game)
        self.assertEqual(status, 200)
        self.assertEqual(len(content['players']), len(invites) + 1)
        self.assertIn('id', content)
        self.game = content

        # invite and accept
        content, status = self.post_as(
            self.users['steve']['token'], '/game/{}/invite'.format(self.game['id']), { 'emails': ['bill@microsoft.com'] }
        )
        self.assertEqual(status, 200)

        content, status = self.post_as(
            self.users['bill']['token'], '/game/{}/add'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(content['started'], False)

        content, status = self.post_as(
            self.users['obama']['token'], '/game/{}/add'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(content['started'], True)

        content, status = self.post_as(
            self.users['steve']['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(content['players']), 3)
        self.assertEqual(len(content['hand']), 10)

        content, status = self.post_as(
            self.users['bill']['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(content['players']), 3)
        self.assertEqual(len(content['hand']), 10)

        players = ['steve', 'bill', 'obama']

        # non-judge players play their cards
        for player in players:
            content, status = self.post_as(
                self.users[player]['token'], '/game/{}'.format(self.game['id']), {}
            )
            self.assertEqual(status, 200)

            if content['judge']['name'] == self.users[player]['name']:
                judge = player
            else:
                content, status = self.post_as(
                    self.users[player]['token'],
                    '/game/{}/play'.format(self.game['id']),
                    { 'cards': [content['hand'][0]['id']] }
                )
                self.assertEqual(status, 200)

        # table is now filled up
        content, status = self.post_as(
            self.users[player]['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(content['table']), 2)

        # try to play a card twice in the same round
        for player in players:
            content, status = self.post_as(
                self.users[player]['token'], '/game/{}'.format(self.game['id']), {}
            )
            self.assertEqual(status, 200)

            if content['judge']['name'] == self.users[player]['name']:
                judge = player
            else:
                content, status = self.post_as(
                    self.users[player]['token'],
                    '/game/{}/play'.format(self.game['id']),
                    { 'cards': [content['hand'][0]['id']] }
                )
                self.assertEqual(status, 418)

        # judge chooses winner
        winner = next(
            (player for player in players if player != judge),
            None
        )
        content, status = self.post_as(
            self.users[judge]['token'],
            '/game/{}/play'.format(self.game['id']),
            { 'email': self.users[winner]['email'] }
        )
        self.assertEqual(status, 200)

        # check previous round
        content, status = self.post_as(
            self.users[player]['token'], '/game/{}'.format(self.game['id']), {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(len(content['table']), 0)

        # new round begins, check for new judge
        content, status = self.post_as(
            self.users[players[0]]['token'],
            '/game/{}'.format(self.game['id']),
            {}
        )
        self.assertNotEqual(judge, content['judge']['name'].split(' ')[0])
        self.assertIn(content['judge']['name'].split(' ')[0], players)
        judge = content['judge']['name'].split(' ')[0]

        # non-judge players play their cards
        for player in players:
            content, status = self.post_as(
                self.users[player]['token'], '/game/{}'.format(self.game['id']), {}
            )
            self.assertEqual(status, 200)

            if content['judge']['name'] == self.users[player]['name']:
                judge = player
            else:
                content, status = self.post_as(
                    self.users[player]['token'],
                    '/game/{}/play'.format(self.game['id']),
                    { 'cards': [content['hand'][0]['id']] }
                )
                self.assertEqual(status, 200)

        # judge chooses winner
        winner = next(
            (player for player in players if player != judge),
            None
        )
        content, status = self.post_as(
            self.users[judge]['token'],
            '/game/{}/play'.format(self.game['id']),
            { 'email': self.users[winner]['email'] }
        )
        self.assertEqual(status, 200)

        # game ended
