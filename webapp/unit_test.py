import unittest
from project import app, db
from project.models import *
import json


class Test(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        pass

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
        # Create another user
        rv = self.app.post('/api/user',
                           data=json.dumps({'username': 'iamawitch'}),
                           content_type='application/json')
        json_data = json.loads(rv.data)
        self.user_id2 = json_data['userid']
        # Ask for the currenct playing games
        rv = self.app.get('/api/games')
        games = json.loads(rv.data)
        assert len(games) > 0
        # Join the first game
        rv = self.app.post('/api/join',
                           data=json.dumps({'game_id': games[0]['game_id'],
                                            'user_id': self.user_id}),
                           content_type='application/json')




if __name__ == '__main__':
    unittest.main()
