from Tanks.AT_SPG import AT_SPG
from Tanks.HEAVY_TANK import HEAVY_TANK
from Tanks.LIGHT_TANK import LIGHT_TANK
from Tanks.MEDIUM_TANK import MEDIUM_TANK
from Tanks.SPG import SPG
from Tanks.Tank import Tank
from Aliases import jsonDict
from Utils import HexToTuple

class TankFactory:
    """
    A class that manages the creation of tanks.
    """
    def __init__(self) -> None:
        """
        Initializes the TankFactory.
        """
        self.__tankTypeMapping = {
            "at_spg": AT_SPG,
            "heavy_tank": HEAVY_TANK,
            "light_tank": LIGHT_TANK,
            "medium_tank": MEDIUM_TANK,
            "spg": SPG,
        }

    def createTank(self, tankData: jsonDict) -> Tank:
        """
        Creates a tank object from the given tank data.

        :param tankData: The data of the tank to create (from the server).
        :return: The newly created Tank object.
        """
        tankType = tankData["vehicle_type"]
        spawnPosition = HexToTuple(tankData["spawn_position"])
        position = HexToTuple(tankData["position"])
        ownerId = tankData["player_id"]
        currentHealth = tankData["health"]
        capturePoints = tankData["capture_points"]
        
        return self.__tankTypeMapping[tankType](spawnPosition, position, ownerId, currentHealth, capturePoints)
