from ServerConnection import ServerConnection
from ServerConnection import Action
from enum import IntEnum
from Map import Map
from Tanks import Tanks
from tkinter import *
import random
import threading

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
        data["game"] = "test105"
        data["num_players"] = 2
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

        If original turn action timed out, we issue more requests. If all of them time out, Exception is raised.
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

    def move(self, message) -> resultDict:
        return self.__handleResult(self.connection.move(message))

    def __exit__(self, *args):
        """
        Close connection to the server socket on exit
        """
        self.connection.close()


mapSemaphore1 = threading.Semaphore(0)
mapSemaphore2 = threading.Semaphore(0)


class GameThread(threading.Thread):
    '''
    Represents the logic of the game running as a separate thread.
    '''

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        print("Name: ", end="")
        name = input()
        with PlayerSession(name) as session:
            playerID = session.login()
            print(playerID)
            gameState = session.getGameState()

            # find all player tanks and create a list that matches turn order
            playerTanks = [None] * len(Tanks.turnOrder)  # TODO : class for general data
            for tankId, tankData in gameState["vehicles"].items():
                if tankData["player_id"] == playerID:
                    playerTanks[Tanks.turnOrder.index(tankData["vehicle_type"])] = tankId

            # Prepare arguments for Map creation.
            mapList.append(session.getMapInfo())
            mapList.append(gameState)
            # Release the semaphore to that the map can be created.
            mapSemaphore1.release()

            # Wait until the map is ready.
            mapSemaphore2.acquire()
            map = mapList[2]

            while not gameState["finished"]:
                # perform other player actions
                gameActions = session.getGameActions()
                for action in gameActions["actions"]:
                    if action["action_type"] == Action.MOVE and action["player_id"] != playerID:
                        actionData = action["data"]
                        map.move(str(actionData["vehicle_id"]), actionData["target"])

                map.testMap(gameState)

                if gameState["current_player_idx"] == playerID:
                    # perform movement with each tank
                    for tankId in playerTanks:
                        moves = map.getMoves(str(tankId))
                        if len(moves) > 0:
                            moveToUse = random.randint(0, len(moves) - 1)
                        else:
                            continue

                        print(f"TankId {tankId}, Possible move count : {len(moves)}, Chosen move : {moves[moveToUse]}")
                        session.move({"vehicle_id": tankId, "target": moves[moveToUse]})
                        map.move(str(tankId), moves[moveToUse])

                session.nextTurn()
                gameState = session.getGameState()
                map.updateMap(gameState)

            # perform other player actions
            gameActions = session.getGameActions()
            for action in gameActions["actions"]:
                if action["action_type"] == Action.MOVE:
                    actionData = action["data"]
                    map.move(str(actionData["vehicle_id"]), actionData["target"])
            print(gameState["winner"])
            session.logout()


mapList = []
if __name__ == "__main__":
    # Start the game thread.
    game = GameThread()
    game.start()
    # Wait until the map is ready to be created.
    mapSemaphore1.acquire()
    gameMap = Map(mapList[0], mapList[1])
    mapList.append(gameMap)
    mapSemaphore2.release()
    gameMap.showMap()
