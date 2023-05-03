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


class ShootingModifier(IntEnum):
    """
    Enumerator that contains modifiers in range[-1, 1] for choosing optimal attack target,
    or to choose whether to attack at all (base value is 0)
    """
    ENOUGH_TO_DESTROY = 0.5
    NOT_ENOUGH_TURNS = -1
    NUMBER_OF_TARGETS = 0.25  # bonus modifier if there are multiple targets
    TANK_ON_CENTRAL_BASE = 1
