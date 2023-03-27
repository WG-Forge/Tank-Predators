from ServerConnection import ServerConnection
from enum import Enum


class Result(Enum):
    """
    Enumerator of all possible result codes given in the docs.
    """
    OKAY = 0
    BAD_COMMAND = 1
    ACCESS_DENIED = 2
    INAPPROPRIATE_GAME_STATE = 3
    TIMEOUT = 4
    INTERNAL_SERVER_ERROR = 500


def login(name: str) -> int:
    """
    Logs the player to the game server.
    :param name: player name
    :return: player id if login was successful, -1 otherwise
    """
    data = dict()
    data["name"] = name
    result = conn.login(data)
    if result["resultCode"] != Result.OKAY.value:
        raise Exception("Login failed")

    return int(result["data"]["idx"])


def gameLoop():
    print("Name: ", end="")
    name = input()
    playerID = login(name)
    print(playerID)
    conn.logout()


if __name__ == "__main__":
    conn = ServerConnection()
    try:
        gameLoop()
    except Exception as e:
        print(e)
    finally:
        conn.close()
