from TankComponents.CurvedShootingComponent import CurvedShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class LIGHT_TANK(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, currentHealth: int = None) -> None:
        super().__init__(spawnPosition, position, Settings.LIGHT_TANK, currentHealth)
  
    def _initializeShooting(self):
        self.components["shooting"] = CurvedShootingComponent(Settings.LIGHT_TANK["minAttackRange"], Settings.LIGHT_TANK["maxAttackRange"], Settings.LIGHT_TANK["damage"])