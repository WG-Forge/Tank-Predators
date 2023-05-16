from Events.Events import TankAddedEvent
from Events.Events import TankShotEvent
from Events.Events import TankDestroyedEvent
from Events.Events import TankRespawnedEvent
from Events.Events import TankRepairedEvent
from Events.EventManager import EventManager
from Tanks.Tank import Tank
import logging

class TankHealthSystem:
    """
    A system that manages the health of tanks.
    """
    def __init__(self, eventManager: EventManager):
        """
        Initializes the TankHealthSystem.

        :param eventManager: The EventManager instance to use for triggering events.
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__eventManager.addHandler(TankShotEvent, self.onTankShot)
        self.__eventManager.addHandler(TankRespawnedEvent, self.onTankRespawned)
        self.__eventManager.addHandler(TankRepairedEvent, self.onTankRepaired)
        self.__tanks = {}

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has a health component

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        healthComponent = tankEntity.getComponent("health")

        if healthComponent:
            self.__tanks[tankId] = healthComponent


    def onTankShot(self, tankId: str, damage: int):
        """
        Event handler. Handles tanks taking damage.

        :param tankId: The ID of the tank that got shot.
        :param damage: Amount of damage.
        """
        healthComponent = self.__tanks.get(tankId)

        if healthComponent:
            healthComponent.currentHealth -= damage

            if healthComponent.currentHealth <= 0:
                self.__eventManager.triggerEvent(TankDestroyedEvent, tankId)

    def __heal(self, healthComponent) -> None:
        """
        Heals a healthComponent object to its maximum health.

        :param healthComponent: The healthComponent object to heal.
        """
        healthComponent.currentHealth = healthComponent.maxHealth        
        
    def onTankRespawned(self, tankId: str) -> None:
        """
        Event handler. Handles healing a tank to full on respawn.

        :param tankId: The ID of the tank that got respawned.
        """
        healthComponent = self.__tanks.get(tankId)

        if healthComponent:
            self.__heal(healthComponent)

    def onTankRepaired(self, tankId: str) -> None:
        """
        Event handler. Handles healing a tank on repair.

        :param tankId: The ID of the tank that got repaired.
        """
        healthComponent = self.__tanks.get(tankId)

        if healthComponent:
            logging.debug(f"Repair used: TankId:{tankId}")
            self.__heal(healthComponent)

    def reset(self) -> None:
        """
        Resets the system to it's initial state.
        """
        self.__tanks.clear()
