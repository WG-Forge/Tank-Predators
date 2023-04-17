from TankManagement.TankFactory import TankFactory
from Events.Events import TankAddedEvent
from Events.EventManager import EventManager
from Tanks.Tank import Tank
from Aliases import jsonDict

class TankManager:
    """
    A class that manages the tanks.
    """
    def __init__(self, eventManager: EventManager) -> None:
        """
        Initializes the TankManager.

        :param eventManager: The EventManager instance to use for registering and triggering events.
        """
        self.__tankFactory = TankFactory()
        self.__eventManager = eventManager
        self.__tanks = {}

    def addTank(self, tankId: str, tankData: jsonDict) -> None:
        """
        Adds a new tank to the manager with the given ID and data, and notifies any observers of the new tank.

        :param tankId: The ID of the tank to add (from the server).
        :param tankData: The data of the tank to add, as a dictionary (from the server).
        """
        self.__tanks[tankId] = self.__tankFactory.createTank(tankData)
        self.__eventManager.triggerEvent(TankAddedEvent, tankId, self.__tanks[tankId])
        
    def hasTank(self, tankId: str) -> bool:
        """
        Checks whether the manager has a tank with the given ID.

        :param tankId: The ID of the tank to check.
        :return: True if the manager has a tank with the given ID, False otherwise.
        """
        return tankId in self.__tanks
        
    def getTank(self, tankId: str) -> Tank:
        """
        Gets the tank entity with the given ID.

        :param tankId: The ID of the tank to get.
        :return: The Tank instance with the given ID.
        """
        return self.__tanks[tankId]
