from Exceptions import BadCommandException, InappropriateGameStateException, TimeoutException, \
    InternalServerErrorException
from PlayerSession import PlayerSession
from Utils import HexToTuple
from Utils import TupleToHex
from ServerConnection import Action
import logging
from Aliases import jsonDict
from World import World

class Game:
    def __init__(self, session: PlayerSession, data: jsonDict) -> None:
        self.__session = session
        self.__playerID = self.__session.login(data)

        # Get static map data
        self.__map = self.__session.getMapInfo()
        self.__gameState = self.__session.getGameState()
        self.__world = World(self.__map, self.__gameState)
        self.__bot = self.__world.getBot()
        self.__initializeTurnOrder()
        self.__previousPlayer = "Unknown"
        self.__turn()
        self.__play()
        self.__session.logout()

    def __initializeTurnOrder(self):
        turnOrder = ["spg", "light_tank", "heavy_tank", "medium_tank", "at_spg"]

        self.__playerTanks = [None] * 5
        for tankId, tankData in self.__gameState["vehicles"].items():
            if tankData["player_id"] == self.__playerID:
                self.__playerTanks[turnOrder.index(tankData["vehicle_type"])] = tankId

    def __reset(self):
        self.__previousPlayer = "Unknown"
        self.__gameState = self.__session.getGameState()
        self.__world.resetSystems(self.__gameState)
        self.__turn()

    def __selfTurn(self):
        self.__bot.getBestTargets(self.__playerTanks)  # calculate best targets to shoot at
        for tankId in self.__playerTanks:
            # perform local player actions
            action, targetPosition = self.__bot.getAction(tankId)
            if action == "shoot":
                self.__session.shoot({"vehicle_id": int(tankId), "target": TupleToHex(targetPosition)})
                self.__world.shoot(tankId, targetPosition)
            elif action == "move":
                self.__session.move({"vehicle_id": int(tankId), "target": TupleToHex(targetPosition)})
                self.__world.move(tankId, targetPosition)

        self.__session.nextTurn()

    def __otherTurn(self):
        # skip turn since it's not our
        self.__session.nextTurn()
        # perform other player actions
        gameActions = self.__session.getGameActions()

        for action in gameActions["actions"]:
            if action["player_id"] == self.__playerID:
                break
            if action["action_type"] == Action.MOVE:
                actionData = action["data"]
                self.__world.move(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))
            elif action["action_type"] == Action.SHOOT:
                actionData = action["data"]
                self.__world.shoot(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))

    def __turn(self) -> None:
        self.__world.addMissingTanks(self.__gameState)
        self.__world.turn(self.__gameState["current_player_idx"])

    def __round(self) -> None:
        if self.__gameState["current_turn"] % self.__gameState["num_players"] == 0:
            self.__world.round()

    def __play(self):
        while not self.__gameState["finished"]:
            try:
                currentPlayer = self.__gameState["current_player_idx"]
                if currentPlayer != self.__previousPlayer:
                    self.__previousPlayer = currentPlayer
                    if currentPlayer == self.__playerID:  # our turn
                        self.__selfTurn()
                    else:
                        self.__otherTurn()
                else:
                    self.__session.nextTurn()

                self.__gameState = self.__session.getGameState()
                self.__turn()
                self.__round()
            except TimeoutException as exception:
                logging.debug(f"TimeoutException:{exception.message}")
            except (InappropriateGameStateException, InternalServerErrorException) as exception:
                logging.debug(f"{exception.__class__.__name__}:{exception.message}")
                self.__reset()
            except BadCommandException as exception:
                logging.debug(f"BadCommandException:{exception.message}")
                self.__session.nextTurn()
                self.__reset()

    def quit(self):
        self.__world.quit()

    def isWinner(self) -> bool:
        return self.__playerID == self.__gameState["winner"]