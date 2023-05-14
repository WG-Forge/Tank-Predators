from Events.Events import TankAddedEvent
from Events.Events import TankMovedEvent
from Events.Events import TankRespawnedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from Aliases import positionTuple

class TankMovementSystem:
    """
    A system that manages the movement of tanks.
    """

    def __init__(self, map: Map, eventManager: EventManager, pathingOffsets: list[dict[tuple[int, int, int], set[tuple[int, int, int]]]]) -> None:
        """
        Initializes the TankMovementSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        :param maxDistance: The maximum distance a tank can travel
        :param pathingOffsets: A list of dictionaries representing all possible positions a target can move to in a given number of steps 
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__eventManager.addHandler(TankRespawnedEvent, self.onTankRespawned)
        self.__map = map
        self.__tankPositions = {}
        self.__tankMap = {}
        self.__spawnPoints = {}
        self.__canMoveTo = {"Empty", "Base", "Catapult", "LightRepair", "HardRepair"}
        self.__pathingOffsets = pathingOffsets

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has a position component

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        positionComponent = tankEntity.getComponent("position")

        if positionComponent:
            self.__tankPositions[tankId] = positionComponent
            self.__tankMap[positionComponent.position] = tankId
            self.__spawnPoints[positionComponent.spawnPosition] = tankId

    def getMovementOptions(self, tankId: str) -> list[positionTuple]:
        """
        Gets all possible moves for a given tank.

        :param tankId: The ID of the tank to get moves for.

        :return: A list of positionTuples representing all possible movement options.
        """
        if tankId not in self.__tankPositions:
            raise ValueError(f"TankId:{tankId} is not in the movement system")
        
        # Gets the tanks maximum movement distance
        distance = self.__tankPositions[tankId].speed
        mapSize = self.__map.getSize()
        startingPosition = self.__tankPositions[tankId].position  # Get starting position to a tuple
        visited = set()  # Set to store visited offsets
        visited.add((0, 0, 0))  # Can always reach 0 offset since the tank is already there
        result = []  # List to store valid movement options

        # Perform breadth-first search to find all possible moves
        for currentDistance in range(1, distance + 1):
            for offsetPosition, canBeReachedBy in self.__pathingOffsets[currentDistance].items():
                if not len(visited.intersection(canBeReachedBy)) > 0:
                    continue # can't be reached

                currentPosition = tuple(x + y for x, y in zip(startingPosition, offsetPosition))
                if not all(abs(pos) < mapSize for pos in currentPosition):
                    continue # outside of map borders

                currentPositionObject = self.__map.objectAt(currentPosition)
                if not currentPositionObject in self.__canMoveTo:
                    continue # tanks can't move there

                visited.add(offsetPosition)
                spawnPoint = self.__spawnPoints.get(currentPosition)
                if currentPosition in self.__tankMap or (spawnPoint is not None and spawnPoint != tankId):
                    continue # tank is already there or it's a different tank's spawnpoint

                result.append(currentPosition)

        return result

    def move(self, tankId: str, newPosition: positionTuple) -> None:
        """
        Move the specified tank to the new position, triggering a moved event.

        :param tankId: The ID of the tank to move.
        :param newPosition: The new position of the tank as a tuple of (x, y, z) coordinates.
        """
        if tankId not in self.__tankPositions:
            raise ValueError(f"TankId:{tankId} is not in the movement system")
        
        self.__tankMap.pop(self.__tankPositions[tankId].position)
        self.__tankMap[newPosition] = tankId
        self.__tankPositions[tankId].position = newPosition
        self.__eventManager.triggerEvent(TankMovedEvent, tankId, newPosition)


    def onTankRespawned(self, tankId: str) -> None:
        """
        Event handler. Handles moving a tank to spawnpoint on respawn.

        :param tankId: The ID of the tank that got respawned.
        """
        positionComponent = self.__tankPositions.get(tankId)

        if positionComponent:
            self.move(tankId, positionComponent.spawnPosition)

    def reset(self) -> None:
        """
        Resets the system to it's initial state.
        """
        self.__tankPositions.clear()
        self.__tankMap.clear()
        self.__spawnPoints.clear()