from enum import IntEnum, Enum

NUM_TANKS = 5  # number of each player tanks


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


class HexTypes(Enum):
    EMPTY = "Empty"
    BASE = "Base"
    OBSTACLE = "Obstacle"
    LIGHT_REPAIR = "LightRepair"
    HARD_REPAIR = "HardRepair"
    CATAPULT = "Catapult"


class TankTypes(Enum):
    AT_SPG = "at_spg"
    HEAVY_TANK = "heavy_tank"
    LIGHT_TANK = "light_tank"
    MEDIUM_TANK = "medium_tank"
    SPG = "spg"
