from abc import ABC, abstractmethod
from Tanks.Components.HealthComponent import HealthComponent
from Tanks.Components.PositionComponent import PositionComponent
from Tanks.Components.DestructionRewardComponent import DestructionRewardComponent
from Tanks.Components.BaseCaptureComponent import BaseCaptureComponent
from Tanks.Components.CurvedShootingComponent import CurvedShootingComponent
from Tanks.Components.OwnerComponent import OwnerComponent
from Aliases import positionTuple
from Aliases import jsonDict

class Tank(ABC):
    """
    Abstract base class for all tank entities in the game.
    """
    __slots__ = ("__components",)

    def __init__(self, spawnPosition: positionTuple, position: positionTuple, ownerId: int, settings: jsonDict, currentHealth: int = None) -> None:
        """
        Initializes a new instance of the Tank class.

        :param spawnPosition: A tuple representing the spawn position of the tank.
        :param position: A tuple representing the current position of the tank.
        :param ownerId: An integer representing the owner of the tank.
        :param settings: A dictionary containing all the settings of the tank entity.
        :param currentHealth: Optional. An integer representing the current health value of the tank.
                            If not provided, it will default to the maximum health value.
        """
        self.__components = {}
        self._initializeOwner(ownerId)
        self._initializePosition(spawnPosition, position, settings["sp"])
        self._initializeDestructionReward(settings["destructionPoints"])
        if currentHealth is None:
            self._initializeHealth(settings["hp"], settings["hp"])
        else:
            self._initializeHealth(settings["hp"], currentHealth)
        self._initializeCapture()
        self._initializeShooting(settings)

    def _initializeOwner(self, ownerId: int) -> None:
        """
        Initializes the owner component for the tank.

        :param ownerId: An integer representing the owner of the tank.
        """
        self._setComponent("owner", OwnerComponent(ownerId))

    def _initializePosition(self, spawnPosition: positionTuple, position: positionTuple, speed: int) -> None:
        """
        Initializes the position component for the tank.

        :param spawnPosition: A tuple representing the spawn position of the tank.
        :param position: A tuple representing the current position of the tank.
        :param speed: An integer representing the speed of the tank.
        """
        self._setComponent("position", PositionComponent(spawnPosition, position, speed))

    def _initializeDestructionReward(self, destructionReward: int) -> None:
        """
        Initializes the destruction reward component for the tank.

        :param destructionReward: An integer representing the reward for destroying the tank.
        """
        self._setComponent("destructionReward", DestructionRewardComponent(destructionReward))

    def _initializeHealth(self, maxHealth: int, currentHealth: int) -> None:
        """
        Initializes the health component for the tank.

        :param maxHealth: An integer representing the maximum health value of the tank.
        :param currentHealth: An integer representing the current health value of the tank.
        """
        self._setComponent("health", HealthComponent(maxHealth, currentHealth))

    def _initializeCapture(self) -> None:
        """
        Initializes the capture component for the tank.
        """
        self._setComponent("capture", BaseCaptureComponent())

    def _initializeShooting(self, settings: jsonDict) -> None:
        """
        Initializes the shooting component for the tank.

        :param settings: A dictionary containing the settings of the tank.
            - "minAttackRange": An integer representing the minimum attack range of the tank.
            - "maxAttackRange": An integer representing the maximum attack range of the tank.
            - "damage": An integer representing the damage dealt by the tank's attacks.
        """
        self._setComponent("shooting", CurvedShootingComponent(settings["minAttackRange"], settings["maxAttackRange"], settings["damage"]))
    
    def getComponent(self, componentName: str) -> object:
        """
        Returns the component instance with the given name.

        :param componentName: A string representing the name of the component to retrieve.
        :return: The component instance with the given name.
        """
        return self.__components[componentName]
    
    def hasComponent(self, componentName: str) -> bool:
        """
        Returns True if the tank has a component with the given name, False otherwise.

        :param componentName: A string representing the name of the component to check for.
        :return: True if the tank has a component with the given name, False otherwise.
        """
        return componentName in self.__components
    
    def _setComponent(self, componentName: str, componentInstance: object) -> None:
        """
        Sets the component instance with the given name to the provided instance.

        :param componentName: A string representing the name of the component to set.
        :param componentInstance: The instance of the component to set.
        """
        self.__components[componentName] = componentInstance