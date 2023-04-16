from Tanks.Components.DirectShootingComponent import DirectShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
from Aliases import jsonDict
import Tanks.Settings as Settings

class AT_SPG(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, ownerId: int, currentHealth: int = None) -> None:
        """
        Initializes a tank destroyer.

        :param spawnPosition: A tuple representing the position where the tank is spawned.
        :param position: A tuple representing the initial position of the tank.
        :param ownerId: An integer representing the owner of the tank.
        :param currentHealth: An optional integer representing the current health of the tank.
        """
        super().__init__(spawnPosition, position, ownerId, Settings.AT_SPG, currentHealth)
  
    def _initializeShooting(self, settings: jsonDict) -> None:
        """
        Overrides initialization of the shooting component for the AT-SPG tank.

        :param settings: A dictionary containing the settings of the tank.
            - "maxAttackDistance": An integer representing the maximum attack distance of the direct shot.
            - "damage": An integer representing the damage dealt by the tank's attacks.
        """
        self._setComponent("shooting", DirectShootingComponent(settings["maxAttackDistance"], settings["damage"]))