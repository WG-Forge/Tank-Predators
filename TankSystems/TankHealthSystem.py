from Events.Events import TankAddedEvent
from Events.Events import TankShotEvent
from Events.Events import TankDestroyedEvent
from Events.Events import TankRespawnedEvent
from Events.EventManager import EventManager
from Tanks.AT_SPG import AT_SPG
from Tanks.HEAVY_TANK import HEAVY_TANK
from Tanks.MEDIUM_TANK import MEDIUM_TANK
from Tanks.Tank import Tank
from Map import Map

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
        self.__eventManager.addHandler(TankRespawnedEvent, self.onTankRespawned)
        self.__tanks = {}
        self.__lightRepair = {MEDIUM_TANK}
        self.__hardRepair = {AT_SPG, HEAVY_TANK}

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has health and position components

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        healthComponent = tankEntity.getComponent("health")
        positionComponent = tankEntity.getComponent("position")

        if healthComponent and positionComponent:
            self.__tanks[tankId] = {
                "health": healthComponent,
                "position": positionComponent,
                "tankType": type(tankEntity),
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

            if healthComponent.currentHealth <= 0:
                self.__eventManager.triggerEvent(TankDestroyedEvent, tankId)

    def __heal(self, tank: Tank) -> None:
        healthComponent = tank["health"]
        healthComponent.currentHealth = healthComponent.maxHealth        
        
    def onTankRespawned(self, tankId: str) -> None:
        """
        Event handler. Handles healing a tank to full on respawn.

        :param tankId: The ID of the tank that got respawned.
        """
        tank = self.__tanks.get(tankId)

        if tank:
            self.__heal(tank)
    
    def turn(self) -> None:
        for tank in self.__tanks.values():
            obj = self.__map.objectAt(tank["position"].position)
            tankType = tank["tankType"]

            if (obj == "LightRepair" and tankType in self.__lightRepair) or (obj == "HardRepair" and tankType in self.__hardRepair):
                self.__heal(tank)

