from Events.Events import TankRespawnedEvent
from Events.Events import TankDestroyedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank

class TankRespawnSystem:
    """
    A system that manages respawning of tanks.
    """
    def __init__(self, eventManager: EventManager):
        """
        Initializes the TankRespawnSystem.

        :param eventManager: The EventManager instance to use for triggering events.
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankDestroyedEvent, self.onTankDestroyed)
        self.__destroyedTankIds = []

    def onTankDestroyed(self, tankId: str):
        """
        Event handler. Handles adding a destroyed tankId to destroyedTankIds.

        :param tankId: The ID of the tank that got destroyed.
        """
        self.__destroyedTankIds.append(tankId)

    def turn(self):
        for tankId in self.__destroyedTankIds:
            self.__eventManager.triggerEvent(TankRespawnedEvent, tankId)
        
        self.__destroyedTankIds.clear()
