from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class HEAVY_TANK(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, ownerId: int, currentHealth: int = None) -> None:
        """
        Initializes a heavy tank.

        :param spawnPosition: A tuple representing the position where the tank is spawned.
        :param position: A tuple representing the initial position of the tank.
        :param ownerId: An integer representing the owner of the tank.
        :param currentHealth: An optional integer representing the current health of the tank.
        """
        super().__init__(spawnPosition, position, ownerId, Settings.HEAVY_TANK, currentHealth)