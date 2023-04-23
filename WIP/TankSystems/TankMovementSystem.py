from Events.Events import TankAddedEvent
from Events.Events import TankMovedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
from Aliases import positionTuple
import itertools

class TankMovementSystem:
    """
    A system that manages the movement of tanks.
    """

    def __init__(self, map: Map, eventManager: EventManager, maxDistance: int) -> None:
        """
        Initializes the TankMovementSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        :param maxDistance: The maximum distance a tank can travel
        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__map = map
        self.__tankPositions = {}
        self.__tankMap = {}
        self.__spawnPoints = {}
        self.__canMoveTo = ["Empty", "Base"]
        self.__canMoveTrough = ["Empty", "Base"]
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__initializePathingOffsets(maxDistance)

    def __initializePathingOffsets(self, maxDistance: int) -> None:
        """
        Calculates pathing offsets to a distance of maximum travel distance of any tank.
        Initializes a list of dictionaries representing all possible positions a tank can move to
        in a given number of steps (i.e., distance) based on the maximum speed of any tank.

        Each dictionary in the '__pathingOffsets' list contains position keys that map to a set of previous
        positions that a tank can move from to reach the position. This information is used later to determine
        possible movement options from any position.
        """

        # Get the maximum travel distance of any tank.
        startingPosition = (0, 0, 0)

        # Keep track of which positions have already been visited.
        visited = set()
        visited.add(startingPosition)

        # The '__pathingOffsets' list will store dictionaries representing reachable positions at each distance.
        self.__pathingOffsets = []
        self.__pathingOffsets.append({startingPosition: {startingPosition}})

        # Perform breadth-first search to find all possible movement options
        for currentDistance in range(1, maxDistance + 1): \
                # Create a new dictionary for the current distance
            self.__pathingOffsets.append({})
            # Iterate over each position in the previous distance to obtain current distance offsets.
            for position in self.__pathingOffsets[currentDistance - 1]:
                for permutation in self.__hexPermutations:
                    nextPosition = tuple(x + y for x, y in zip(position, permutation))
                    # If the next position has not been visited before (is not reachable by another source),
                    # add it to the current distance and add the position as its source.
                    if not nextPosition in visited:
                        self.__pathingOffsets[currentDistance][nextPosition] = {position}
                        visited.add(nextPosition)
                    # If the next position has already been added to the current distance (is already reachable by another source but at the same distance),
                    # add the position to the existing set of source positions.
                    elif nextPosition in self.__pathingOffsets[currentDistance]:
                        self.__pathingOffsets[currentDistance][nextPosition].add(position)

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

    def getMovementOptions(self, tankId: str):
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
            # Iterate over all possible offsets for the current distance
            for offsetPosition, canBeReachedBy in self.__pathingOffsets[currentDistance].items():
                # Check if the offset can be reached from a previously reachable position
                if len(visited.intersection(canBeReachedBy)) > 0:
                    currentPosition = tuple(x + y for x, y in zip(startingPosition, offsetPosition))
                    # Check if the current position is within the boundaries of the game map
                    if abs(currentPosition[0]) < mapSize and abs(currentPosition[1]) < mapSize and abs(
                            currentPosition[2]) < mapSize:
                        currentPositionObject = self.__map.objectAt(currentPosition)
                        # Check if the tank can move through the current position
                        if currentPositionObject in self.__canMoveTrough:
                            visited.add(offsetPosition)
                            # Check if the tank can move to the current position and if there is no other tank in that position
                            if currentPositionObject in self.__canMoveTo and not currentPosition in self.__tankMap:
                                spawnPoint = self.__spawnPoints.get(currentPosition)
                                # Check if the current position is a spawnpoint
                                if spawnPoint is not None:
                                    # Check if the spawn point doesn't belong to the current tank
                                    if spawnPoint != tankId:
                                        continue
                                # Add current position to the result list
                                result.append(currentPosition)

        return result

    def move(self, tankId: str, newPosition: positionTuple):
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
