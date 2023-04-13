import itertools
from Tanks import *
from Utils import HexToTuple
from Utils import TupleToHex
from typing import List

jsonDict = dict[str, any] # alias
from HexGrid import *
from tkinter import *

class Map():
    """
    A class representing a map in the game.

    Attributes:
        __hexPermutations (List[Tuple[int, int, int]]): A list of all possible permutations of 
            -1, 0, and 1 that are used to calculate possible moves.
        __canMoveTo (List[str]): A list of tile types that tanks can move to.
        __canMoveTrough (List[str]): A list of tile types that tanks can move through.
        __size (int): The size of the map.
        __name (str): The name of the map.
        __spawnPoints (Dict[Tuple[int, int, int], str]): A dictionary mapping spawn points to tank names.
        __map (Dict[Tuple[int, int, int], str]): A dictionary representing the map, 
            mapping hex coordinates to tile types.
        __tanks (Dict[str, jsonDict]): A dictionary representing the tanks on the map,
            mapping tank IDs to tank data.

    Methods:
        __initializeSpawnPoints(allPlayerSpawnPoints: jsonDict) -> None:
            Initializes the map's spawn points.
        __initializeBase(base: jsonDict) -> None:
            Initializes the map's base.
        __initializeTanks(vehicles: jsonDict) -> None:
            Initializes the map's tanks.
        isBase(hex: jsonDict) -> bool:
            Determines whether a given hex cell is part of a base on the map.
        getMoves(tankId: str) -> List[jsonDict]:
            Gets all possible moves for a given tank.
        move(tankId: str, hex: jsonDict) -> None:
            Moves a given tank to a given hex cell.
    """

    def __init__(self, map : jsonDict, gameState : jsonDict) -> None:
        """
        Initializes a Map object with the data provided by the game server.
        
        :param map: A dictionary containing the map data.
        :param gameState: A dictionary containing the current state of the game.
        """
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__canMoveTo = ["Empty", "Base"]
        self.__canMoveTrough = ["Empty", "Base"]

        self.__playerCount = gameState["num_players"]
        self.__size = map["size"]
        self.__name = map["name"]
        self.__initializeMapContent(map["content"])
        self.__initializeSpawnPoints(map["spawn_points"])
        self.__initializeTanks(gameState["vehicles"])
        self.__initializePathingOffsets()
        self.__teamColors = ["orange", "purple", "blue"]
        self.__colors = {
            "Base" : "green",
            "Obstacle" : "gray"
        }
        self.__drawMap()


    def __initializeSpawnPoints(self, allPlayerSpawnPoints : jsonDict) -> None:
        '''
        Initializes the spawn points on the map.

        :param allPlayerSpawnPoints: A dictionary containing the spawn points for all players.
        '''
        self.__spawnPoints = {}

        for playerSpawnPoints, playerIndex in zip(allPlayerSpawnPoints, range(self.__playerCount)):
            tankId = 5 * playerIndex + 1
            for tankSpawnPoints in playerSpawnPoints.values():
                    self.__spawnPoints[str(tankId)] = tankSpawnPoints

                    for spawnPoint in tankSpawnPoints:
                        self.__map[HexToTuple(spawnPoint)] = str(tankId)
                        self.__canMoveTrough.append(str(tankId))

                    tankId += 1


    def __initializeMapContent(self, mapContent : jsonDict) -> None:
        '''
        Initializes the map content.

        :param base: A dictionary containing the map content for the map.
        '''
        self.__map = {}

        for baseHex in mapContent["base"]:
            self.__map[HexToTuple(baseHex)] = "Base"

        for obstacleHex in mapContent["obstacle"]:
            self.__map[HexToTuple(obstacleHex)] = "Obstacle"


    def __initializeTanks(self, vehicles : jsonDict) -> None:
        '''
        Initializes the tanks on the map.

        :param vehicles: A dictionary containing the vehicle data for the map.
        '''
        self.__tanks = vehicles
        self.__tankMap = {}
        
        for tankId, tankInfo in self.__tanks.items():
            self.__tankMap[HexToTuple(tankInfo["position"])] = tankId


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
        maxDistance = max(tank["sp"] for tank in Tanks.allTanks.values())
        startingPosition = (0, 0, 0)

        # Keep track of which positions have already been visited.
        visited = set() 
        visited.add(startingPosition)

        # The '__pathingOffsets' list will store dictionaries representing reachable positions at each distance.
        self.__pathingOffsets = [] 
        self.__pathingOffsets.append({startingPosition : {startingPosition}}) 

        # Perform breadth-first search to find all possible movement options
        for currentDistance in range(1, maxDistance + 1):\
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


    def __setCell(self, position : tuple, fillColor : str) -> None:
        '''
        Sets a cell to a given color on the map.

        :param position: Position tuple of the cell to change
        :param fillColor: Color to fill the cell with
        '''
        offsetCoordinates = cube_to_offset(position[0], position[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=fillColor)


    def __drawMap(self) -> None:
        '''
        Draws the map in it's initial form.
        '''
        self.__window = Tk()
        self.__window.title(self.__name + " on HexTanks")
        self.__grid = HexagonalGrid(self.__window, hexaSize=20, grid_width=self.__size, grid_height=self.__size)
        self.__grid.grid(row=0, column=0, padx=5, pady=5)

        draw_grid(self.__grid, self.__size, 0, 0)
        grid_set.clear()

        # draw the map
        for position, name in self.__map.items():
            self.__setCell(position, self.__colors.get(name, "white"))

        # draw tanks 
        for playerIndex in range(self.__playerCount):
            startTankId = playerIndex * 5 + 1
            for tankId in range(startTankId, startTankId + 5):
                if str(tankId) in self.__tanks:
                    self.__setCell(HexToTuple(self.__tanks[str(tankId)]["position"]), self.__teamColors[playerIndex])           
                else:
                    self.__setCell(HexToTuple(self.__spawnPoints[str(tankId)][0]), self.__teamColors[playerIndex])      


    def isBase(self, hex : jsonDict) -> bool:
        '''
        Determines whether a given hex cell is part of a base on the map.

        :param hex: A dictionary containing the coordinates of the hex cell to check.

        :return: True if the hex cell is part of a base, False otherwise.
        '''
        if self.__map.get(HexToTuple(hex), "Empty") == "Base":
            return True
        
        return False
    

    def getMoves(self, tankId : str) -> List[jsonDict]:
        '''
        Gets all possible moves for a given tank.

        :param tankId: The ID of the tank to get moves for.

        :return: A list of JSON dictionaries representing all possible movement options.
        '''

        # Get the tank type and its speed points
        tank = Tanks.allTanks[self.__tanks[tankId]["vehicle_type"]]
        distance = tank["sp"]

        startingPosition = HexToTuple(self.__tanks[tankId]["position"]) # Convert starting position to a tuple
        visited = set() # Set to store visited offsets
        visited.add((0, 0, 0)) # Can always reach 0 offset since the tank is already there
        result = [] # List to store valid movement options

        # Perform breadth-first search to find all possible moves
        for currentDistance in range(1, distance + 1):
            # Iterate over all possible offsets for the current distance
            for offsetPosition, canBeReachedBy in self.__pathingOffsets[currentDistance].items():
                    # Check if the offset can be reached from a previously reachable position
                    if len(visited.intersection(canBeReachedBy)) > 0:
                        currentPosition = tuple(x + y for x, y in zip(startingPosition, offsetPosition))
                        # Check if the current position is within the boundaries of the game map
                        if abs(currentPosition[0]) < self.__size and abs(currentPosition[1]) < self.__size and abs(currentPosition[2]) < self.__size:                      
                            currentPositionObject = self.__map.get(currentPosition, "Empty")
                            # Check if the tank can move through the current position
                            if currentPositionObject in self.__canMoveTrough:
                                visited.add(offsetPosition)
                                # Check if the tank can move to the current position and if there is no other tank in that position
                                if (currentPositionObject in self.__canMoveTo or currentPositionObject == tankId) and not currentPosition in self.__tankMap:
                                    # Convert the current position to a dict representation and add it to the result list
                                    result.append(TupleToHex(currentPosition))

        return result
    

    def move(self, tankId : str, position : jsonDict) -> None:
        '''
        Moves a given tank to a given hex cell

        :param tankId: Id of the tank to get moves for.
        :param hex: Hex cell to move the tank to
        '''
        # Draw an empty cell.
        currentPosition = HexToTuple(self.__tanks[tankId]["position"])
        self.__setCell(currentPosition, self.__colors.get(self.__map.get(currentPosition), "white"))
        self.__tankMap.pop(currentPosition)

        # Draw an occupied cell.
        newPosition = HexToTuple(position)
        self.__setCell(newPosition, self.__teamColors[(int(tankId) - 1) // 5])
        self.__tankMap[newPosition] = tankId

        self.__tanks[tankId]["position"] = position


    def showMap(self) -> None:
        '''
        Shows the window on which the map is presented.
        '''
        self.__window.mainloop()
    

    def updateMap(self, gameState: jsonDict) -> None:
        '''
        This method checks if there are any new tanks in the game state that are not present in the local tanks list.
        If a new tank is found, it is added to the local tanks list, and its position is added to the map.
        Additionally, the tank is added to the list of tanks that can be moved through.
        '''
        for tankId, tankInfo in gameState["vehicles"].items():
            tankId = str(tankId)

            if tankId not in self.__tanks:
                print("New tank inserted")
                self.__tanks[tankId] = tankInfo
                self.__canMoveTrough.append(tankId)
                tankPosition = HexToTuple(tankInfo["position"])
                self.__tankMap[tankPosition] = tankId
                self.__setCell(tankPosition, self.__teamColors[(int(tankId) - 1) // 5])


    def testMap(self, gameState: jsonDict) -> None:
        '''
        This method compares the positions of the tanks in the game state with their positions in the local tanks list.
        If a tank is found to be miss positioned, its cell on the grid is updated and a message is sent to the console.
        The local tanks list and the map are also updated with the correct position of the tank.
        '''
        for tankId, tankInfo in gameState["vehicles"].items():
            tankId = str(tankId)

            localTankPosition = self.__tanks[tankId]["position"]
            serverTankPosition = tankInfo["position"]
            if HexToTuple(localTankPosition) != HexToTuple(serverTankPosition):
                print(f"Position error: TankId:{tankId} is at:{localTankPosition} should be:{serverTankPosition}")
                self.move(tankId, serverTankPosition)