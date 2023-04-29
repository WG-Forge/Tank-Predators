from Events.Events import TankAddedEvent
from Events.Events import TankRangeBonusEvent
from Events.Events import TankRepairedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from Tanks.AT_SPG import AT_SPG
from Tanks.HEAVY_TANK import HEAVY_TANK
from Tanks.MEDIUM_TANK import MEDIUM_TANK

class PositionBonusSystem:
    """
    A system that manages position bonuses.
    """

    def __init__(self, map: Map, eventManager: EventManager) -> None:
        """
        Initializes the PositionBonusSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__map = map
        self.__tanks = {}
        self.__lightRepair = {MEDIUM_TANK}
        self.__hardRepair = {AT_SPG, HEAVY_TANK}

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has a position component

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        positionComponent = tankEntity.getComponent("position")

        if positionComponent:
            self.__tanks[tankId] = {
                "position": positionComponent,
                "tankType": type(tankEntity),
            }

    def turn(self):
        for tankId, tankData in self.__tanks.items():
            obj = self.__map.objectAt(tankData["position"].position)
            tankType = tankData["tankType"]

            if (obj == "LightRepair" and tankType in self.__lightRepair) or (obj == "HardRepair" and tankType in self.__hardRepair):
                self.__eventManager.triggerEvent(TankRepairedEvent, tankId)
            elif obj == "Catapult":
                 self.__eventManager.triggerEvent(TankRangeBonusEvent, tankId)