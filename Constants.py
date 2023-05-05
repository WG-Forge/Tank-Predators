from enum import IntEnum


class Result(IntEnum):
    """
    Enumerator of all possible result codes given in the docs.
    """
    OKAY = 0
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500

    def __eq__(self, other):
        if isinstance(other, Result):
            return self.value == other.value

        return self.value == other  # if it's int


class Action(IntEnum):
    LOGIN = 1
    LOGOUT = 2
    MAP = 3
    GAME_STATE = 4
    GAME_ACTIONS = 5
    TURN = 6
    CHAT = 100
    MOVE = 101
    SHOOT = 102


class ActionModifier(IntEnum):
    """
    Enumerator that contains modifiers to choose whether to attack or move
    (positive value -> move, negative value -> shoot)
    """
    CENTRAL_BASE_IN_MOVEMENT_RANGE = -1
    HEALING_IN_RANGE_DESTROY_THREAT = -1  # needs healing and there is a threat to destroy tank
    HEALING_IN_RANGE_NO_THREAT = -0.5  # needs healing but there is no threat to destroy tank
    DESTROY_THREAT = -0.99  # there is a threat to destroy tank, won't move if tank is at central base
    ALLY_TANK_ON_CENTRAL_BASE = 1  # our tank is at the central base
    ENOUGH_TO_DESTROY = 1  # we can destroy enemy tank
    NUMBER_OF_TARGETS = 0.334  # bonus modifier if there are multiple targets(if there is 3 targets bonus is >1)
    ENEMY_TANK_ON_CENTRAL_BASE = 0.7


class ShootingPriority(IntEnum):
    CAPTURED_POINTS = 1  # one for each captured point
    IS_IN_BASE = 1  # tank is in central base
    CAN_BE_DESTROYED = 1  # if tank can be destroyed
    MULTIPLE_TANKS_NEEDED_PENALTY = -0.25  # for each tank needed
    ENEMY_ATTACKED_US = 1  # if enemy player attacked us in the last turn
    ENEMY_PLAYER_CAPTURED_POINTS = 2
