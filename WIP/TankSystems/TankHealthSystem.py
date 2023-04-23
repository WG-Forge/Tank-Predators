from Events.Events import TankAddedEvent
from Events.Events import TankShotEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank

class TankHealthSystem:
    """
    A system that manages the health of tanks.
    """
    def __init__(self, map: Map, eventManager: EventManager):
        """
        Initializes the TankHealthSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        """
        self.__map = map
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__eventManager.addHandler(TankShotEvent, self.onTankShot)
        self.__tanks = {}

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has a health and position components

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        healthComponent = tankEntity.getComponent("health")
        positionComponent = tankEntity.getComponent("position")

        if healthComponent and positionComponent:
            self.__tanks[tankId] = {
                "position": positionComponent,
                "health": healthComponent
            }

    def onTankShot(self, tankId: str, damage: int):
        """
        Event handler. Handles tanks taking damage.

        :param tankId: The ID of the tank that got shot.
        :param damage: Amount of damage.
        """
        tank = self.__tanks.get(tankId)

        if tank:
            healthComponent = tank["health"]
            healthComponent.currentHealth -= damage
