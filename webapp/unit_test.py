import unittest
from project import app, db
import json


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
        self.user_id = json_data['userid']
        # Create a game
        rv = self.app.post('/api/game',
                           data=json.dumps({'game_name': 'witch_game',
                                            'user_id': self.user_id}),
                           content_type='application/json')
        json_data = json.loads(rv.data)
        assert json_data['game_name'] == "witch_game"
        self.game_id = json_data['game_id']
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
        # Number of players should be 11
        # Start the game.
        self.app.post('/api/start_game',
                      data=json.dumps({'game_id': games[0]['game_id']}),
                      content_type='application/json')

        # Request the main view
        game_id = games[0]['game_id']
        rv = self.app.get('/api/main_view', query_string={'game_id': game_id})
        json_data = json.loads(rv.data)
        assert len(json_data['users']) == 10
        assert json_data['game_id'] == game_id
        assert json_data['game_name'] == "witch_game"

        # Request the user view
        rv = self.app.get('/api/user_view', query_string={'user_id': userid})
        print(rv.data)

if __name__ == '__main__':
    unittest.main()
