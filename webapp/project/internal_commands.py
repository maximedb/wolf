from project import db
from project.models import UserType, Round, RoundType
import random
from datetime import datetime, timedelta

mapping = {'wolf': UserType.wolf, 'seer': UserType.seer,
           'hunter': UserType.seer, 'cupid': UserType.cupid,
           'witch': UserType.witch, 'girl': UserType.little_girl}


def allocate_users(game):
    """
    Allocates every user in the database to a specific type according to a
    predifinied allocation table.
    """
    # First take all the users
    users = game.players
    # Should first count the number of users in the game.
    print(users)
    num_users = len(users)
    # Check if the minimum number of users if met.
    if num_users < 6:
        raise RuntimeError('Number of users is not big enough.')
    if num_users > 18:
        raise RuntimeError('Number of users is too big.')
    alloc = [
        {'wolf': 2, 'seer': 1},  # 6 - 3 villagers
        {'wolf': 2, 'seer': 1, 'hunter': 1},  # 7- 3 villagers
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1},  # 8 - 3 villagers
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1},  # 9
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 4, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 4, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 5, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
    ]

    # According to the number of players, choose the right line.
    right_alloc = alloc[num_users - 6]
    # Randomize the users
    randomized_users = random.sample(users, len(users))
    # Assign a class to each one.
    pointer = 0
    # For each key in the alloc table
    for key in right_alloc.keys():
        # For the number of roles available within this key.
        for j in range(right_alloc[key]):
            # Take a random user
            user = randomized_users[pointer]
            # Change its type
            user.type_player = mapping[key]
            # Increment the pointer
            pointer += 1
    # For the remaining players, assign villager type.
    for i in range(pointer, num_users):
        randomized_users[i].type_player = UserType.villager
    # Commit changes to the database
    db.session.commit()


def onboard_user(user):
    """ Given a new user, assigns a player type """
    choices = random.shuffle(mapping)
    user.type_player = choices[0]
    db.session.commit()


def new_round(game, delta=timedelta(minutes=15), day=True):
    """ Create a new round """
    type = RoundType.day if day else RoundType.night
    round = Round(game_id=game.id, round_type=type, start_time=datetime.now(),
                  end_time=datetime.now()+delta)
    game.rounds.append(round)
    db.session.commit()
    return "OK"
