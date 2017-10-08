from flask import request, jsonify
from project import app, db
from project.models import User, Game
from datetime import datetime, timedelta
from project.internal_commands import allocate_users, new_round, vote_for
from project.internal_commands import check_end_of_round


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
    Returns:
        - game_id (int): the id of the game
    """
    # Get the data
    data = request.get_json()
    if 'game_name' not in data:
        return 'please provide a name for the game', 400
    if (len(data['game_name']) <= 0) | ((len(data['game_name']) > 80)):
        return 'please adapt the game name, too long', 400
    game = Game(game_name=data['game_name'])
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
    if user.game is not None:
        return 'User already joined a game', 400
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


@app.route('/api/start_game', methods=['POST'])
def start_game():
    """
    Start the game
    Args:
        - game_id (int): the game to start
    """
    data = request.get_json()
    if 'game_id' not in data:
        return 'Provide a game id please', 400
    game = Game.query.get(data['game_id'])
    if game is None:
        return 'Invalid game', 400
    game.started = True
    game.start_time = datetime.now()
    allocate_users(game)
    new_round(game)
    db.session.commit()
    return "Started"


@app.route('/api/main_state', methods=['GET'])
def main_state():
    """
    Main view to get the general data about a game.
    Returns:
        - game_id (int): the game id
        - game_name (str): the name of the current game
        - end_time (datetime): the time at which the current rounds ends.
        - users [{username(str), alive(boolean)}]: the users in the game
    """
    game_id = request.args.get('game_id')
    if game_id is None:
        return 'Please provide a game_id', 400
    game = Game.query.get(game_id)
    if game is None:
        return 'Wrong game_id', 400
    # Check if this round should end now
    ended = check_end_of_round(game)
    if ended:
        # The previous round ended, start a new one.
        new_round(game)
    players = game.players
    users = [{'user_name': u.username, 'status': u.alive, 'user_id': u.id}
             for u in players]
    current_round = game.rounds[-1]
    end_time = current_round.end_time.isoformat()
    return jsonify({'game_id': game.id, 'game_name': game.game_name,
                    'end_time': end_time, 'users': users,
                    'status': game.started, 'round_id': current_round.id,
                    'round_type': current_round.round_type.name})


@app.route('/api/user_state', methods=['GET'])
def user_state():
    """
    Returns the user data
    Args:
        - user_id (int): the user id
    Returns:
        - round_type (str): the current round_type
        - game_id (int): the game id
        - user_type (int): the type of the user
        - action_required (boolean): should the user do something
        - action_data ([]): present if an action is required
    """
    user_id = request.args.get('user_id')
    if user_id is None:
        return 'Please provide a game_id', 400
    user = User.query.get(user_id)
    if user is None:
        return 'Wrong user', 400
    game = user.game
    current_round = game.rounds[-1]
    round_type = current_round.round_type
    return jsonify({'round_type': round_type.name,
                    'game_id': game.id,
                    'user_type': user.type_player.name,
                    'action_required': False})


@app.route('/api/vote', methods=['POST'])
def vote():
    """
    Function to vote for a player.
    Args:
        - user_from_id (int): the user that votes
        - user_to_id (int): the user that gets nominated
        - game_id (int): the game that is currently played
    """
    data = request.get_json()
    if 'user_from_id' not in data:
        return 'Specify a user from', 400
    if 'user_to_id' not in data:
        return 'Specify a user to', 400
    user_from = User.query.get(data['user_from_id'])
    if user_from is None:
        return 'User id not correct', 400
    user_to = User.query.get(data['user_to_id'])
    if user_to is None:
        return 'User id is not correct', 400
    if 'game_id' not in data:
        return 'Please provide a game id', 400
    game = Game.query.get(data['game_id'])
    if game is None:
        return 'Please provide a valid game id', 400
    vote = vote_for(game, user_from, user_to)
    db.session.add(vote)
    db.session.commit()
    return jsonify({'vote_id': vote.id})


@app.route('/api/end_of_round', methods=['GET'])
def end_of_round():
    game_id = request.args.get('game_id')
    if game_id is None:
        return 'Please provide a game id', 400
    game = Game.query.get(game_id)
    print(game.rounds)
    if game is None:
        return 'Please provide a valid game id', 400
    ended, data = check_end_of_round(game)
    new_round(game)
    return "OK"


@app.route('/api/end_round', methods=['POST'])
def end_round():
    """
    End the current round for a game.
    Args:
        - game_id (int): the game
    """
    data = request.get_json()
    game_id = data['game_id']
    game = Game.query.get(game_id)
    latest_round = game.rounds[-1]
    latest_round.end_time = datetime.utcnow()
    db.session.commit()
    return jsonify({'end_time': latest_round.end_time.isoformat()})
