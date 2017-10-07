from project import db
from project.models import *


def allocate_users(game):
    """
    Allocates every user in the database to a specific type according to a
    predifinied allocation table.
    """
    # First take all the users
    users = game.users
    # Should first count the number of users in the game.
    num_users = len(users)
    # Check if the minimum number of users if met.
    if num_users < 6:
        raise RuntimeError('Number of users is not big enough.')
    alloc = [
        {'wolf': 2, 'seer': 1},  # 6 - 3 villagers
        {'wolf': 2, 'seer': 1, 'hunter': 1},  # 7- 3 villagers
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1},  # 8 - 3 villagers
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1},  # 9
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'gril': 1},
        {'wolf': 2, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 3, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 4, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 4, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
        {'wolf': 5, 'seer': 1, 'hunter': 1, 'cupid': 1, 'witch': 1, 'girl': 1},
    ]
