from TankComponents.CurvedShootingComponent import CurvedShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
import Tanks.Settings as Settings

class SPG(Tank):
    __slots__ = ()

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, currentHealth: int = None) -> None:
        super().__init__(spawnPosition, position, Settings.SPG["sp"], Settings.SPG["hp"], currentHealth)

    def _initializeShooting(self):
        self.components["shooting"] = CurvedShootingComponent(Settings.SPG["minAttackRange"], Settings.SPG["maxAttackRange"], Settings.SPG["damage"])