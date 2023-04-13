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
        visited = set() # Set to store visited hexes
        visited.add(startingPosition) 
        result = [] # List to store valid movement options

        fringes = [] # A list of lists of hexes representing positions at each distance from starting position
        fringes.append([startingPosition]) # Add starting position as the first fringe (distance = 0)


        # Perform breadth-first search to find all possible moves
        for currentDistance in range(1, distance + 1):
            fringes.append([]) # Add a new fringe for each distance

            for position in fringes[currentDistance - 1]:
                for permutation in self.__hexPermutations:
                    nextPosition = tuple(x + y for x, y in zip(position, permutation))

                    # Check if the next position is within the boundaries of the game map
                    if abs(nextPosition[0]) < self.__size and abs(nextPosition[1]) < self.__size and abs(nextPosition[2]) < self.__size:                      
                        nextPositionObject = self.__map.get(nextPosition, "Empty")

                        # Check if it has not been visited before and if the tank can move through the next position
                        if not nextPosition in visited and nextPositionObject in self.__canMoveTrough:
                            fringes[currentDistance].append(nextPosition)
                            visited.add(nextPosition)

                            # Check if the tank can move to the next position and if there is no other tank in that position
                            if (nextPositionObject in self.__canMoveTo or nextPositionObject == tankId) and not nextPosition in self.__tankMap:
                                result.append(TupleToHex(nextPosition))

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