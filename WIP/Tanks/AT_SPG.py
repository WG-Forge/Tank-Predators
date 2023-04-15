from TankComponents.DirectShootingComponent import DirectShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class AT_SPG(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, currentHealth: int = None) -> None:
        super().__init__(spawnPosition, position, Settings.AT_SPG["sp"], Settings.AT_SPG["hp"], currentHealth)
  
    def _initializeShooting(self):
        self.components["shooting"] = DirectShootingComponent(Settings.AT_SPG["maxAttackDistance"], Settings.AT_SPG["damage"])