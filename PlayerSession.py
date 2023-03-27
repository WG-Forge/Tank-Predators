from ServerConnection import ServerConnection
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


class PlayerSession:
    __slots__ = ("name", "connection")  # class members

    def __init__(self, name):
        self.name = name
        self.connection = ServerConnection()


    def login(self) -> int:
        """
        Logs the player to the game server.
        :return: player id if login was successful, -1 otherwise
        """
        data = dict()
        data["name"] = self.name
        result = self.connection.login(data)
        if result["resultCode"] != Result.OKAY:
            raise Exception("Login failed")

        return int(result["data"]["idx"])

    def logout(self):
        """
        Logs out the player and removes the player's record from the server storage.
        """
        self.connection.logout()


    def __del__(self):
        """
        Before deleting object, closes connection to the server socket
        """
        self.connection.close()


def gameLoop():
    print("Name: ", end="")
    name = input()
    session = PlayerSession(name)
    playerID = session.login()
    print(playerID)
    session.logout()


if __name__ == "__main__":
    try:
        gameLoop()
    except Exception as e:
        print(e)
