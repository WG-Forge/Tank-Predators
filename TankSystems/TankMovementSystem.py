from Events.Events import TankAddedEvent
from Events.Events import TankMovedEvent
from Events.Events import TankRespawnedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from Aliases import positionTuple
from collections import deque
import itertools

class TankMovementSystem:
    """
    A system that manages the movement of tanks.
    """

    def __init__(self, map: Map, eventManager: EventManager) -> None:
        """
        Initializes the TankMovementSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        :param maxDistance: The maximum distance a tank can travel
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__eventManager.addHandler(TankRespawnedEvent, self.onTankRespawned)
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__map = map
        self.__mapSize = map.getSize()
        self.__tankPositions = {}
        self.__tankMap = {}
        self.__spawnPoints = {}
        self.__canMoveTo = {"Empty", "Base", "Catapult", "LightRepair", "HardRepair"}

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
        startingPosition = self.__tankPositions[tankId].position

        visited = set()  # Set to store visited positions
        visited.add(startingPosition) 
        result = []  # List to store valid movement options
        queue = deque()
        queue.append(((startingPosition), 0))
        visited.add(startingPosition)

        # Perform breadth-first search to find all possible moves
        while len(queue) > 0:
            currentPosition, currentDistance = queue.popleft()
            currentPositionObject = self.__map.objectAt(currentPosition)
            if not (currentPositionObject in self.__canMoveTo):
                continue

            spawnPoint = self.__spawnPoints.get(currentPosition)
            if not currentPosition in self.__tankMap and (spawnPoint is None or spawnPoint == tankId):
                result.append(currentPosition)

            if currentDistance + 1 > distance:
                continue

            for permutation in self.__hexPermutations:
                newPosition = tuple(x + y for x, y in zip(currentPosition, permutation))
                if all(abs(pos) < self.__mapSize for pos in newPosition) and not newPosition in visited:
                    visited.add(newPosition)
                    queue.append(((newPosition), currentDistance + 1))

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