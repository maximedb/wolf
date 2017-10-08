import unittest
from project import app, db
from project.models import UserType, RoundType
import json
import time


class Test(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()

    def test_new_user(self):
        # Create a first user
        rv = self.app.post('/api/user',
                           data=json.dumps({'username': 'maaax'}),
                           content_type='application/json')
        json_data = json.loads(rv.data)
        user_id = json_data['userid']

        # Create a game
        rv = self.app.post('/api/game',
                           data=json.dumps({'game_name': 'witch_game',
                                            'user_id': user_id}),
                           content_type='application/json')
        json_data = json.loads(rv.data)
        assert json_data['game_name'] == "witch_game"
        game_id = json_data['game_id']

        # Ask for the currenct playing games
        rv = self.app.get('/api/games')
        games = json.loads(rv.data)
        assert len(games) > 0

        # Create multiple users and make them join the game
        for i in range(10):
            # Create another user
            rv = self.app.post('/api/user',
                               data=json.dumps({'username': 'user'+str(i)}),
                               content_type='application/json')
            json_data = json.loads(rv.data)
            userid = json_data['userid']
            # Join the first game
            rv = self.app.post('/api/join',
                               data=json.dumps({'game_id': games[0]['game_id'],
                                                'user_id': userid}),
                               content_type='application/json')

        # Start the game.
        rv = self.app.post('/api/start_game',
                           data=json.dumps({'game_id': games[0]['game_id']}),
                           content_type='application/json')

        # Request the main view
        game_id = games[0]['game_id']
        rv = self.app.get('/api/main_state', query_string={'game_id': game_id})
        json_data = json.loads(rv.data)
        users = json_data['users']
        assert len(json_data['users']) == 10
        assert json_data['game_id'] == game_id
        assert json_data['game_name'] == "witch_game"
        assert json_data['status'] is True

        # Request the user view
        rv = self.app.get('/api/user_state', query_string={'user_id': userid})
        json_data = json.loads(rv.data)
        assert json_data['game_id'] == game_id
        assert json_data['round_type'] == 'night'

        # Take all the wolf players.
        # For each player, ask the user view and record the user_type
        for i in range(len(users)):
            uid = users[i]['user_id']
            rv = self.app.get('/api/user_state', query_string={'user_id': uid})
            json_data = json.loads(rv.data)
            users[i]['user_type'] = json_data['user_type']
        # Target to vote against
        for user in users:
            if user['user_type'] != 'wolf':
                target = user
        # Make all the wolves vote for the target
        for user in users:
            if user['user_type'] == 'wolf':
                self.app.post('/api/vote',
                              data=json.dumps({'user_from_id': user['user_id'],
                                               'user_to_id': target['user_id'],
                                               'game_id': game_id}),
                              content_type='application/json')
        # End the round.
        rv = self.app.post('/api/end_round',
                           data=json.dumps({'game_id': game_id}),
                           content_type='application/json')
        json_data = json.loads(rv.data)
        print(json_data)
        # Check the status -> should still be running
        # time.sleep(2)
        # Check the status
        query_string = {'game_id': game_id}
        rv = self.app.get('/api/main_state', query_string=query_string)
        json_data = json.loads(rv.data)
        dead_users = [u for u in json_data['users'] if u['status'] is False]
        print(json_data)
        assert json_data['round_id'] == 2
        assert json_data['round_type'] == 'day'
        assert len(dead_users) == 1
        assert dead_users[0]['user_id'] == target['user_id']

        # Day time. Everybody votes for the first non dead player
        # Let's try to make the dead guy vote.
        dead_guy = dead_users[0]
        with self.assertRaises(Exception):
            rv = self.app.post('/api/vote',
                               data=json.dumps(
                                    {'user_from_id': dead_guy['user_id'],
                                     'user_to_id': dead_guy['user_id'],
                                     'game_id': game_id}),
                               content_type='application/json')
        # Everybody except the dead guy will vote for the 
        target = users[0]


if __name__ == '__main__':
    unittest.main()
