from ServerConnection import ServerConnection
from enum import IntEnum

resultDict = dict[str, any]  # result dictionary type


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
    __slots__ = ("name", "connection")  # class members

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.connection = ServerConnection()
        return self

    @staticmethod
    def __handleResult(result):
        """
        Handles error codes and returns data if request was successful
        :param result: result dict from action request with "resultCode" and "data" keys
        :return: result["data"] if the result was Okay,
        None if it was TIMEOUT error.
        Exception is raised for other error types.
        """
        code = result["resultCode"]
        if code == Result.BAD_COMMAND or code == Result.INAPPROPRIATE_GAME_STATE or code == Result.ACCESS_DENIED or code == Result.INTERNAL_SERVER_ERROR:
            raise Exception("ERROR: " + (Result(code)).name)  # example: ERROR: BAD_COMMAND
        elif code == Result.TIMEOUT:
            return None  # Action should be requested again
        return result["data"]

    def login(self) -> int:
        """
        Logs the player to the game server.
        :return: player id if login was successful, -1 otherwise
        """
        data = dict()
        data["name"] = self.name
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

        If original turn action timed out, we issue more request. If all of them time out, Exception is raised.
        :return:
        """
        for i in range(100):
            result = self.__handleResult(self.connection.turn())
            if result is not None:
                break
        else:  # if all requests Timed out.
            raise Exception("ERROR: TIMEOUT")

    def getMapInfo(self) -> resultDict:
        """
        Returns the game map. Map represents static information about the game.
        :return: data about the map
        """
        return self.__handleResult(self.connection.map())

    def getGameActions(self) -> resultDict:
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

    def getGameState(self) -> resultDict:
        """
        Returns the current state of the game. The game state represents dynamic information about the game.
        The game state is updated at the end of a turn.
        :return: dictionary with game state
        """
        return self.__handleResult(self.connection.game_state())

    def __exit__(self, *args):
        """
        Close connection to the server socket on exit
        """
        self.connection.close()


def gameLoop():
    print("Name: ", end="")
    name = input()
    with PlayerSession(name) as session:
        playerID = session.login()
        gameState = session.getGameState()

        while not gameState["finished"]:
            if gameState["current_player_idx"] == playerID:
                session.nextTurn()
            gameState = session.getGameState()

        print(gameState["winner"])
        session.logout()


if __name__ == "__main__":
    try:
        gameLoop()
    except Exception as e:
        print(e)