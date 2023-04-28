from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class SPG(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, ownerId: int, currentHealth: int, capturePoints: int) -> None:
        """
        Initializes an SPG (Self-propelled artillery).

        :param spawnPosition: A tuple representing the position where the tank is spawned.
        :param position: A tuple representing the initial position of the tank.
        :param ownerId: An integer representing the owner of the tank.
        :param currentHealth: An integer representing the current health of the tank.
        :param capturePoints: An integer representing the capture points of the tank.
        """
        super().__init__(spawnPosition, position, ownerId, currentHealth, capturePoints, Settings.TANKS["SPG"])