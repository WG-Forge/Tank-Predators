from Tanks.AT_SPG import AT_SPG
from Tanks.HEAVY_TANK import HEAVY_TANK
from Tanks.LIGHT_TANK import LIGHT_TANK
from Tanks.MEDIUM_TANK import MEDIUM_TANK
from Tanks.SPG import SPG
from Tanks.Tank import Tank
from Aliases import jsonDict
from Utils import HexToTuple

class TankManager:
    """
    A class that manages the tanks in a game.
    """

    def __init__(self) -> None:
        """
        Initializes the TankManager object.
        """
        self.__tanks = {}
        self.__tankTypeMapping = {
            "at_spg": AT_SPG,
            "heavy_tank": HEAVY_TANK,
            "light_tank": LIGHT_TANK,
            "medium_tank": MEDIUM_TANK,
            "spg": SPG,
        }
       
    def addTank(self, tankId: str, tankData: jsonDict) -> None:
        """
        Adds a tank to the manager with the given tank ID and data.

        :param tankId: The ID of the tank to add.
        :param tankData: The data of the tank to add.
        """
        tankType = tankData["vehicle_type"]
        spawnPosition = HexToTuple(tankData["spawn_position"])
        position = HexToTuple(tankData["position"])
        ownerId = tankData["player_id"]
        currentHealth = tankData["health"]
        capturePoints = tankData["capture_points"]
        
        self.__tanks[tankId] = self.__tankTypeMapping[tankType](spawnPosition, position, ownerId, currentHealth, capturePoints)
        
    def hasTank(self, tankId: str) -> bool:
        """
        Checks whether the manager has a tank with the given ID.

        :param tankId: The ID of the tank to check.
        :return: True if the manager has a tank with the given ID, False otherwise.
        """
        return tankId in self.__tanks
    
    def getTank(self, tankId: str) -> Tank:
        """
        Gets the tank entity with the given ID.

        :param tankId: The ID of the tank to get.
        :return: The tank entity with the given ID.
        """
        return self.__tanks[tankId]