from TankManagement.TankManager import TankManager
from TankManagement.TankAddedEvent import TankAddedEvent
from Tanks.Tank import Tank
from Aliases import jsonDict
from typing import Callable

class TankManagementSystem:
    """
    A class that adds subject functionality to TankManager, allowing it to notify its observers when a new tank is added."
    """

    def __init__(self) -> None:
        """
        Initializes the TankManagementSystem.
        """
        self.__tankManager = TankManager()
        self.__tankAddedEvent = TankAddedEvent()

    def addTank(self, tankId: str, tankData: jsonDict) -> None:
        """
        Adds a tank to the manager with the given tank ID and data, and notifies any observers of the new tank.

        :param tankId: The ID of the tank to add.
        :param tankData: The data of the tank to add.
        """
        self.__tankManager.addTank(tankId, tankData)
        self.__tankAddedEvent.raiseEvent(tankId, self.__tankManager.getTank(tankId))
        
    def hasTank(self, tankId: str) -> bool:
        """
        Checks whether the manager has a tank with the given ID.

        :param tankId: The ID of the tank to check.
        :return: True if the manager has a tank with the given ID, False otherwise.
        """
        return self.__tankManager.hasTank(tankId)
        
    def getTank(self, tankId: str) -> Tank:
        """
        Gets the tank entity with the given ID.

        :param tankId: The ID of the tank to get.
        :return: The tank entity entity with the given ID.
        """
        return self.__tankManager.getTank(tankId)
    
    def addTankAddedHandler(self, handler: Callable[[str, Tank], None]) -> None:
        """
        Adds a new handler to the tank added event.

        :param handler: The handler function to add.
        """
        self.__tankAddedEvent.addHandler(handler)

    def removeTankAddedHandler(self, handler: Callable[[str, Tank], None]) -> None:
        """
        Removes a handler from the tank added event.

        :param handler: The handler function to remove.
        """
        self.__tankAddedEvent.removeHandler(handler)
