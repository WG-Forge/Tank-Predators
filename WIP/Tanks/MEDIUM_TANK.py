from TankComponents.CurvedShootingComponent import CurvedShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class MEDIUM_TANK(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, currentHealth: int = None) -> None:
        super().__init__(spawnPosition, position, Settings.MEDIUM_TANK, currentHealth)

    def _initializeShooting(self):
        self.components["shooting"] = CurvedShootingComponent(Settings.MEDIUM_TANK["minAttackRange"], Settings.MEDIUM_TANK["maxAttackRange"], Settings.MEDIUM_TANK["damage"])
  
