from flask import request, jsonify, Response
from project import app, db
from project.models import User, Game
from datetime import datetime, timedelta


@app.route('/api/user', methods=['POST'])
def create_user():
    """
    Create a new user. Checks if the username is still available.
    Args:
        - username (string): a user name
    Returns:
        - userid (int): a user id
        - username (string): the username
    """
    # JSON data from the post request
    data = request.get_json()
    print(data)
    # Check if the user provided a username
    if 'username' not in data:
        return 'please provide a user_name', 400
    # Check if the provided username is already used
    username = data['username']
    user = User.query.filter_by(username=data['username']).first()
    # If the result is not None, there already is a user with the same name
    if user is not None:
        # Counter to increment the name by one
        counter = 0
        # While there is someone with the same name, increment the counter
        while user is not None:
            username = data['username'] + '_' + str(counter)
            user = User.query.filter_by(username=username).first()
            counter += 1
        # Ok we have a free username
        user = User(username=username)
    else:
        # The username was not already taken, we can proceeed
        user = User(username=username)
    # Add the new user to the session
    db.session.add(user)
    # Commit to the database
    db.session.commit()
    # Return the object to the client.
    return jsonify({'userid': user.id, 'username': user.username})


@app.route('/api/game', methods=['POST'])
def create_game():
    """
    Create a new game. Must give a user_id that admins the room.
    Args:
        - game_name (string): a name for the game_name
        - user_id (int): the admin of the game_name
    Returns:
        - game_id (int): the id of the game
    """
    # Get the data
    data = request.get_json()
    # Check that there is a user_id in
    if 'user_id' not in data:
        return 'please provide a user', 400
    if 'game_name' not in data:
        return 'please provide a name for the game', 400
    user = User.query.get(data['user_id'])
    if user is None:
        return 'please provide a valid user', 400
    if (len(data['game_name']) <= 0) | ((len(data['game_name']) > 80)):
        return 'please adapt the game name, too long', 400
    game = Game(admin=user.id, game_name=data['game_name'])
    user.game_id = game.id
    db.session.add(game)
    db.session.commit()
    return jsonify({'game_id': game.id, 'game_name': game.game_name})


@app.route('/api/join', methods=['POST'])
def join_game():
    """
    Join a game.
    args:
        - game_id (int): the game to join
        - user_id (int): the user that wants to join
    returns:
        - game_id (int): the game id
    """
    data = request.get_json()
    if 'game_id' not in data:
        return 'please provide a game_id', 400
    if 'user_id' not in data:
        return 'please provide a user_id', 400
    user = User.query.get(data['user_id'])
    if user is None:
        return 'please provide a valid user', 400
    game = Game.query.get(data['game_id'])
    if game is None:
        return 'please provide a valid game', 400
    user.game = game
    db.session.add(user)
    db.session.commit()
    return jsonify({'game_id': game.id})


@app.route('/api/games', methods=['GET'])
def list_games():
    """
    List the current playing games (less than 12h old)
    Returns:
        - games ([{game_id: int, game_name: string}]): the games
    """
    start_time = datetime.now() - timedelta(hours=12)
    games = Game.query.filter(Game.start_time >= start_time).all()
    games_j = [{'game_id': g.id, 'game_name': g.game_name} for g in games]
    return jsonify(games_j)
