from abc import ABC, abstractmethod
from TankComponents.HealthComponent import HealthComponent
from TankComponents.PositionComponent import PositionComponent
from TankComponents.DestructionRewardComponent import DestructionRewardComponent
from TankComponents.BaseCaptureComponent import BaseCaptureComponent
from Aliases import positionTuple

class Tank(ABC):
    """
    Abstract base class for all tank entities in the game.
    """
    __slots__ = ("components",)

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, settings: dict[str, any], currentHealth: int = None) -> None:
        """
        Initializes a new instance of the Tank class.

        :param spawnPosition: A tuple representing the spawn position of the tank.
        :param position: A tuple representing the current position of the tank.
        :param settings: A dictionary containing all the settings of the tank entity.
        :param currentHealth: Optional. An integer representing the current health value of the tank.
                            If not provided, it will default to the maximum health value.
        """
        self.components = {}
        self._initializePosition(spawnPosition, position, settings["sp"])
        self._initializeDestructionReward(settings["destructionPoints"])
        self._initializeHealth(settings["hp"], currentHealth)
        self._initializeCapture()
        self._initializeShooting()

    def _initializePosition(self, spawnPosition: positionTuple, position: positionTuple, speed: int):
        """
        Initializes the position component for the tank.

        :param spawnPosition: A tuple representing the spawn position of the tank.
        :param position: A tuple representing the current position of the tank.
        :param speed: An integer representing the speed of the tank.
        """
        self.components["position"] = PositionComponent(spawnPosition, position, speed)

    def _initializeDestructionReward(self, destructionReward: int):
        """
        Initializes the destruction reward component for the tank.

        :param destructionReward: An integer representing the reward for destroying the tank.
        """
        self.components["destructionReward"] = DestructionRewardComponent(destructionReward)

    def _initializeHealth(self, maxHealth: int, currentHealth: int = None):
        """
        Initializes the health component for the tank.

        :param maxHealth: An integer representing the maximum health value of the tank.
        :param currentHealth: Optional. An integer representing the current health value of the tank.
                            If not provided, it will default to the maximum health value.
        """
        self.components["health"] = HealthComponent(maxHealth, currentHealth)

    def _initializeCapture(self):
        """
        Initializes the capture component for the tank.
        """
        self.components["capture"] = BaseCaptureComponent()

    @abstractmethod
    def _initializeShooting(self):
        """
        Initializes the shooting component for the tank.

        This method should be implemented by the inheriting classes.
        """
        pass
