from TankComponents.CurvedShootingComponent import CurvedShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class HEAVY_TANK(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, currentHealth: int = None) -> None:
        super().__init__(spawnPosition, position, Settings.HEAVY_TANK["sp"], Settings.HEAVY_TANK["hp"], currentHealth)
  
    def _initializeShooting(self):
        self.components["shooting"] = CurvedShootingComponent(Settings.HEAVY_TANK["minAttackRange"], Settings.HEAVY_TANK["maxAttackRange"], Settings.HEAVY_TANK["damage"])