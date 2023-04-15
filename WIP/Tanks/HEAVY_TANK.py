from TankComponents.CurvedShootingComponent import CurvedShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class HEAVY_TANK(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, currentHealth: int = None) -> None:
        super().__init__(spawnPosition, position, Settings.HEAVY_TANK, currentHealth)