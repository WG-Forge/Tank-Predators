from ServerConnection import ServerConnection
from enum import IntEnum
from Aliases import jsonDict
from Exceptions import BadCommandException, AccessDeniedException, InappropriateGameStateException, TimeoutException, InternalServerErrorException

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

class PlayerSession:
    __slots__ = ("name", "password", "connection", "__errorMapping")  # class members

    def __init__(self, name, password):
        self.name = name
        self.password = password
        self.__errorMapping = {
            Result.BAD_COMMAND.value: BadCommandException,
            Result.ACCESS_DENIED.value: AccessDeniedException,
            Result.INAPPROPRIATE_GAME_STATE.value: InappropriateGameStateException,
            Result.TIMEOUT.value: TimeoutException,
            Result.INTERNAL_SERVER_ERROR.value: InternalServerErrorException
        }

    def __enter__(self):
        self.connection = ServerConnection()
        return self

    def __handleResult(self, result):
        """
        Handles error codes and returns data if request was successful
        :param result: result dict from action request with "resultCode" and "data" keys
        :return: result["data"] if the result was okay,
        Exception is raised for error types.
        """
        code = result["resultCode"]
        if code != Result.OKAY:
            raise self.__errorMapping[code](result["data"]["error_message"])

        return result["data"]

    def login(self, data: jsonDict) -> int:
        """
        Logs the player to the game server.
        :return: player id if login was successful, -1 otherwise
        """
        data["name"] = self.name

        if self.password:
            data["password"] = self.password

        result = self.__handleResult(self.connection.login(data))

        return int(result["idx"])

    def logout(self):
        """
        Logs out the player and removes the player's record from the server storage.
        """
        self.connection.logout()

    def nextTurn(self):
        """
        Sends a TURN action, which forces the next turn of the game.
        This allows players to play faster and not wait for the game's time slice.
        The game's time slice is 10 seconds for test battles and 1 second for final battles. All players and observers
        must send the TURN action before the next turn can happen.
        """
        return self.__handleResult(self.connection.turn())

    def getMapInfo(self) -> jsonDict:
        """
        Returns the game map. Map represents static information about the game.
        :return: data about the map
        """
        return self.__handleResult(self.connection.map())

    def getGameActions(self) -> jsonDict:
        """
        Gets a list of game actions that happened in the previous turn, representing changes between turns.

        :return: data about the game actions
        """
        return self.__handleResult(self.connection.game_actions())

    def sendChatMessage(self, message):
        """
        Do nothing. Just for testing and fun.
        :param message: message to be sent
        """
        data = dict()
        data["message"] = message
        self.__handleResult(self.connection.chat(data))

    def getGameState(self) -> jsonDict:
        """
        Returns the current state of the game. The game state represents dynamic information about the game.
        The game state is updated at the end of a turn.
        :return: dictionary with game state
        """
        return self.__handleResult(self.connection.game_state())

    def move(self, data) -> jsonDict:
        """
        Changes vehicle position.
        :param data:
        The server expects to receive the following required values:
        vehicle_id - id of vehicle.
        target - coordinates of hex.
        """
        return self.__handleResult(self.connection.move(data))

    def shoot(self, data):
        """
        Shoot to target position.

        :param data:
        The server expects to receive following required values:
        vehicle_id - id of vehicle.
        target - coordinates of hex.
        example: {"vehicle_id":5,"target":{"x":-1,"y":1,"z":0}}
        For AT-SPG target means the direction of shooting,
        and it must be neighboring the AT-SPG's position hex.
        """
        return self.__handleResult(self.connection.shoot(data))

    def __exit__(self, *args):
        """
        Close connection to the server socket on exit
        """
        self.connection.close()