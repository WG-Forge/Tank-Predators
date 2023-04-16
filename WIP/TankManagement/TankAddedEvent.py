from typing import Callable

class TankAddedEvent:
    """
    A class that represents an event that is raised when a new tank is added to the manager.
    """
    
    def __init__(self) -> None:
        """
        Initializes the TankAddedEvent object.
        """
        self.__handlers = []

    def addHandler(self, handler: Callable[[str, object], None]) -> None:
        """
        Adds a new handler to the event.

        :param handler: The handler function to add.
        """
        self.__handlers.append(handler)

    def removeHandler(self, handler: Callable[[str, object], None]) -> None:
        """
        Removes a handler from the event.

        :param handler: The handler function to remove.
        """
        if handler in self.__handlers:
            self.__handlers.remove(handler)

    def raiseEvent(self, tankId: str, tankEntity: object) -> None:
        """
        Raises the event, calling all registered handlers with the given arguments.

        :param tankId: The ID of the new tank.
        :param tankEntity: The tank entity object of the new tank.
        """
        for handler in self.__handlers:
            handler(tankId, tankEntity)