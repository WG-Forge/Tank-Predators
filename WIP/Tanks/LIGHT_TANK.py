from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class LIGHT_TANK(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, currentHealth: int = None) -> None:
        """
        Initializes a light tank.

        :param spawnPosition: A tuple representing the position where the tank is spawned.
        :param position: A tuple representing the initial position of the tank.
        :param currentHealth: An optional integer representing the current health of the tank.
        """
        super().__init__(spawnPosition, position, Settings.LIGHT_TANK, currentHealth)