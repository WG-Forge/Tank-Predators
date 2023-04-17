from Events.Events import TankAddedEvent
from Events.EventManager import EventManager
from Map import Map
from Tanks.Tank import Tank
import Tanks.Settings as TankSettings
from Aliases import positionTuple
import itertools

class TankMovementSystem:
    """
    A system that manages the movement of tanks.
    """

    def __init__(self, map: Map, eventManager: EventManager) -> None:
        """
        Initializes the TankMovementSystem.

        """
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__map = map
        self.__tanks = {}
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__initializePathingOffsets()

    def __initializePathingOffsets(self) -> None:
        """
        Calculates pathing offsets to a distance of maximum travel distance of any tank.
        Initializes a list of dictionaries representing all possible positions a tank can move to
        in a given number of steps (i.e., distance) based on the maximum speed of any tank.

        Each dictionary in the '__pathingOffsets' list contains position keys that map to a set of previous
        positions that a tank can move from to reach the position. This information is used later to determine
        possible movement options from any position.
        """

        # Get the maximum travel distance of any tank.
        maxDistance = max ([tank["sp"] for tank in TankSettings.TANKS.values()])
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

    # TODO: handle new tank addition
    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        pass

    # TODO: obtain and return movement options using map and tanks
    def getMovementOptions(self, tankId: str, tankEntity: Tank):
        pass

    #TODO: change tanks position component if the move is valid
    def move(self, tankId: str, position: positionTuple):
        pass
