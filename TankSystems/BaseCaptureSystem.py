from Events.Events import TankAddedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from Constants import HexTypes


class BaseCaptureSystem:
    """
    A system that base capture.
    """

    def __init__(self, map: Map, eventManager: EventManager) -> None:
        """
        Initializes the BaseCaptureSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__map = map
        self.__tanks = {}

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has position, owner and capture components.

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        positionComponent = tankEntity.getComponent("position")
        captureComponent = tankEntity.getComponent("capture")
        ownerComponent = tankEntity.getComponent("owner")

        if positionComponent and ownerComponent and captureComponent:
            self.__tanks[tankId] = {
                "owner": ownerComponent.ownerId,
                "position": positionComponent,
                "capture": captureComponent,
            }

    def turn(self) -> None:
        """
        Performs the turn logic for the system. 
        
        Resets capture points for tanks that aren't in base hex.
        """
        for tankData in self.__tanks.values():
            obj = self.__map.objectAt(tankData["position"].position)

            if obj != HexTypes.BASE.value:
                tankData["capture"].capturePoints = 0

    def __getCapturingTanks(self) -> tuple[set[int], list[str]]:
        """
        Gets a list of tanks that are inside a base hex and a set of owners of these tanks.

        Returns:
            A tuple containing:
            - A set of integers representing the ownerIds of the capturing tanks.
            - A list of strings representing the IDs of the capturing tanks.
        """
        ownerIds = set()
        capturingTanks = []

        for tankId, tankData in self.__tanks.items():
            obj = self.__map.objectAt(tankData["position"].position)

            if obj == HexTypes.BASE.value:
                capturingTanks.append(tankId)
                ownerIds.add(tankData["owner"])

        return ownerIds, capturingTanks

    def round(self) -> None:
        """
        Performs the round logic for the system.
        
        Adds a capture point to each tank in the base if there are no more than two different owners of these tanks.
        """

        ownerIds, capturingTanks = self.__getCapturingTanks()

        if len(ownerIds) <= 2:
            for capturingTank in capturingTanks:
                self.__tanks[capturingTank]["capture"].capturePoints += 1

    def reset(self) -> None:
        """
        Resets the system to it's initial state.
        """
        self.__tanks.clear()
