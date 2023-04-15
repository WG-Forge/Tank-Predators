from abc import ABC, abstractmethod
from TankComponents.HealthComponent import HealthComponent
from TankComponents.MovementComponent import MovementComponent
from Aliases import positionTuple

class Tank(ABC):
    """
    Abstract base class for all tank entities in the game.
    """
    __slots__ = ("components",)

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, speed: int, maxHealth: int, currentHealth: int = None) -> None:
        """
        Initializes a new instance of the Tank class.

        :param spawnPosition: A tuple representing the spawn position of the tank.
        :param position: A tuple representing the current position of the tank.
        :param speed: An integer representing the speed of the tank.
        :param maxHealth: An integer representing the maximum health value of the tank.
        :param currentHealth: Optional. An integer representing the current health value of the tank.
                            If not provided, it will default to the maximum health value.
        """
        self.components = {}
        self._initializeMovement(spawnPosition, position, speed)
        self._initializeHealth(maxHealth, currentHealth)
        self._initializeShooting()

    def _initializeMovement(self, spawnPosition: positionTuple, position: positionTuple, speed: int):
        """
        Initializes the movement component for the tank.

        :param spawnPosition: A tuple representing the spawn position of the tank.
        :param position: A tuple representing the current position of the tank.
        :param speed: An integer representing the speed of the tank.
        """
        self.components["movement"] = MovementComponent(spawnPosition, position, speed)

    def _initializeHealth(self, maxHealth: int, currentHealth: int = None):
        """
        Initializes the health component for the tank.

        :param maxHealth: An integer representing the maximum health value of the tank.
        :param currentHealth: Optional. An integer representing the current health value of the tank.
                            If not provided, it will default to the maximum health value.
        """
        self.components["health"] = HealthComponent(maxHealth, currentHealth)

    @abstractmethod
    def _initializeShooting(self):
        """
        Initializes the shooting component for the tank.

        This method should be implemented by the inheriting classes.
        """
        pass
