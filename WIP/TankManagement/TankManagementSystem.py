from TankManagement.TankManager import TankManager
from Aliases import jsonDict

class TankManagementSystem:
    """
    A class that adds subject functionality to TankManager, allowing it to notify its observers when a new tank is added."
    """

    def __init__(self) -> None:
        """
        Initializes the TankManagementSystem object.
        """
        self.__tankManager = TankManager()
        self.__observers = []

    def addTank(self, tankId: str, tankData: jsonDict) -> None:
        """
        Adds a tank to the manager with the given tank ID and data, and notifies any observers of the new tank.

        :param tankId: The ID of the tank to add.
        :param tankData: The data of the tank to add.
        """
        self.__tankManager.addTank(tankId, tankData)
        self.__notifyObservers(tankId, self.__tankManager.getTank(tankId))
        
    def hasTank(self, tankId: str) -> bool:
        """
        Checks whether the manager has a tank with the given ID.

        :param tankId: The ID of the tank to check.
        :return: True if the manager has a tank with the given ID, False otherwise.
        """
        return self.__tankManager.hasTank(tankId)
        
    def getTank(self, tankId: str) -> object:
        """
        Gets the tank object with the given ID.

        :param tankId: The ID of the tank to get.
        :return: The tank entity object with the given ID.
        """
        return self.__tankManager.getTank(tankId)
    
    def addObserver(self, observer: object) -> None:
        """
        Adds an observer to the list of observers that will be notified when a new tank is added to the manager.

        :param observer: The observer object to add.
        """
        self.__observers.append(observer)

    def __notifyObservers(self, tankId: str, tankEntity: object) -> None:
        """
        Notifies all observers of the new tank that was added to the manager.

        :param tankId: The ID of the new tank.
        :param tankEntity: The tank entity object of the new tank.
        """
        for observer in self.__observers:
            observer.onTankAdded(tankId, tankEntity)
