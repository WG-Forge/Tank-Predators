from Aliases import jsonDict
from Entity import Entity
from Observer import Observer
from Player import Player


class PlayerManagementSystem:
    __slots__ = ("__players", "__observers")

    def __init__(self, gameState: jsonDict):
        self.__players = {}  # dict[playerIDs, playerObject]
        self.__observers = {}  # dict[observerIDs, observerObject]
        self.__initAllEntities(gameState)

    def __initAllEntities(self, gameState: jsonDict):
        for player in gameState["players"]:
            idx = player["idx"]
            name = player["name"]
            if player["is_observer"]:
                self.__observers = Observer(idx, name)
            else:
                playerTanks = self.__initPlayerTanks(idx, gameState)
                self.__players["idx"] = Player(idx, name, playerTanks)

    @staticmethod
    def __initPlayerTanks(playerId: int, gameState: jsonDict):
        turnOrder = ["spg", "light_tank", "heavy_tank", "medium_tank", "at_spg"]

        playerTanks = [None] * 5
        for tankId, tankData in gameState["vehicles"].items():
            if tankData["player_id"] == playerId:
                playerTanks[turnOrder.index(tankData["vehicle_type"])] = tankId

        return playerTanks
