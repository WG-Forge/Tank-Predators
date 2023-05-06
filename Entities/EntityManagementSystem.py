from Aliases import jsonDict
from Entities.Observer import Observer
from Entities.Player import Player


class EntityManagementSystem:
    __slots__ = ("__players", "__observers", "__tankManager")

    def __init__(self, gameState: jsonDict):
        self.__players = {}  # dict[playerIDs, playerObject]
        self.__observers = {}  # dict[observerIDs, observerObject]
        self.__initAllEntities(gameState)

    def __initAllEntities(self, gameState: jsonDict):
        for player in gameState["players"]:
            idx = player["idx"]
            name = player["name"]
            if player["is_observer"]:
                self.__observers[idx] = Observer(idx, name)
            else:
                playerTanks = self.__initPlayerTanks(idx, gameState)
                self.__players[idx] = Player(idx, name, playerTanks)

    def addMissingEntities(self, gameState: jsonDict):
        for entity in gameState["players"]:
            if entity["idx"] in self.__players or entity["idx"] in self.__observers.keys:
                continue

            idx = entity["idx"]
            name = entity["name"]
            if entity["is_observer"]:
                self.__observers[idx] = Observer(idx, name)
            else:
                playerTanks = self.__initPlayerTanks(idx, gameState)
                self.__players[idx] = Player(idx, name, playerTanks)

    @staticmethod
    def __initPlayerTanks(playerId: int, gameState: jsonDict):
        turnOrder = ["spg", "light_tank", "heavy_tank", "medium_tank", "at_spg"]

        playerTanks = [None] * 5
        for tankId, tankData in gameState["vehicles"].items():
            if tankData["player_id"] == playerId:
                playerTanks[turnOrder.index(tankData["vehicle_type"])] = tankId

        return playerTanks

    def getPlayers(self):
        return self.__players

    def getObservers(self):
        return self.__observers

    def getPlayer(self, playerId: int) -> Player | None:
        if playerId in self.__players:
            return self.__players[playerId]
        return None

    def getObserver(self, observerId: int) -> Observer | None:
        if observerId in self.__observers:
            return self.__players[observerId]
        return None

    def reset(self) -> None:
        self.__players.clear()
        self.__observers.clear()

    def turn(self, gameState):
        currentPlayer = str(gameState["current_player_idx"])
        capturePoints = gameState["win_points"][currentPlayer]["capture"]
        destructionPoints = gameState["win_points"][currentPlayer]["kill"]
        self.__players[int(currentPlayer)].turn(capturePoints, destructionPoints)
