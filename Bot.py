from Map import Map
from Aliases import positionTuple
import math

class Bot:
    settings = {
        "CaptureDistanceMultiplier": 0.95
    }

    def __init__(self, map: Map, pathingOffsets):
        """
        Initializes the TankShootingSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        :param pathingOffsets: A list of dictionaries representing all possible positions a target can move to in a given number of steps 
        """
        self.__map = map
        self.__pathingOffsets = pathingOffsets
        self.__canMoveTo = {"Empty", "Base", "Catapult", "LightRepair", "HardRepair"}
        self.__initializeMap() 

    def __initializeMap(self):
        """
        Gets all possible moves for a given tank.

        :param tankId: The ID of the tank to get moves for.
        """

        self.__valueMap = {}

        for position, obj in self.__map:
            if obj == "Base":
                self.__pathFromBase(position)

    def __pathFromBase(self, basePosition: positionTuple):
        # Gets the tanks maximum movement distance
        distance = self.__map.getSize()
        mapSize = distance
        distanceMultiplier = Bot.settings["CaptureDistanceMultiplier"]
        visited = set()  # Set to store visited offsets
        visited.add((0, 0, 0))  # Can always reach 0 offset since we are already there
        self.__valueMap[basePosition] = 1

        # Perform breadth-first search to find all possible moves
        for currentDistance in range(1, distance + 1):
            # Iterate over all possible offsets for the current distance
            for offsetPosition, canBeReachedBy in self.__pathingOffsets[currentDistance].items():
                # Check if the offset can be reached from a previously reachable position
                if len(visited.intersection(canBeReachedBy)) > 0:
                    currentPosition = tuple(x + y for x, y in zip(basePosition, offsetPosition))
                    # Check if the current position is within the boundaries of the game map
                    if abs(currentPosition[0]) < mapSize and abs(currentPosition[1]) < mapSize and abs(
                            currentPosition[2]) < mapSize:
                        currentPositionObject = self.__map.objectAt(currentPosition)
                        # Check if the tank can move through the current position
                        if currentPositionObject in self.__canMoveTo and currentPositionObject != "Base":
                            currentValue = self.__valueMap.get(currentPosition, -math.inf)
                            newValue = distanceMultiplier**(currentDistance - 1)
                            if newValue >= currentValue:
                                visited.add(offsetPosition)
                                self.__valueMap[currentPosition] = newValue

    def getBestMove(self, moves: list) -> list[positionTuple]:
        maxValue = -math.inf
        maxPositions = []

        for move in moves:
            value = self.__valueMap[move]
            if value > maxValue:
                maxPositions.clear()
                maxPositions.append(move)
                maxValue = value
            elif value == maxValue:
                maxPositions.append(move)

        return maxPositions


            

                   
