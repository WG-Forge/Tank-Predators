import itertools
from Tanks import *
from Utils import HexToTuple
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

        # draw tanks 
        for playerIndex in range(self.__playerCount):
            startTankId = playerIndex * 5 + 1
            for tankId in range(startTankId, startTankId + 5):
                if str(tankId) in self.__tanks:
                    position = HexToTuple(self.__tanks[str(tankId)]["position"])
                    offsetCoordinates = cube_to_offset(position[0], position[1])
                    self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=self.__teamColors[playerIndex])            
                else:
                    position = HexToTuple(self.__spawnPoints[str(tankId)][0])
                    offsetCoordinates = cube_to_offset(position[0], position[1])
                    self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=self.__teamColors[playerIndex])

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

        :return: A list with all possible movement options.
        '''

        # Gets the data for the tank and its speed points
        tank = Tanks.allTanks[self.__tanks[tankId]["vehicle_type"]]
        depth = tank["sp"]

        # Creates a queue to keep track of hex cells to visit
        queue = []
        queue.append(self.__tanks[tankId]["position"])
        popsLeft = 1
        possibleMoves = []

        while len(queue) > 0:
            currentHex = queue.pop(0)
            popsLeft -= 1
            possibleMoves.append(currentHex)

            if depth > 0:
                # Checks the neighbors of the current hex cell and adds them to the queue if they are valid moves
                for permutation in self.__hexPermutations:
                    nextHex = {}
                    nextHex["x"] = currentHex["x"] + permutation[0]
                    nextHex["y"] = currentHex["y"] + permutation[1]
                    nextHex["z"] = currentHex["z"] + permutation[2]

                    if not nextHex in possibleMoves and not nextHex in queue and abs(nextHex["x"]) < self.__size and abs(nextHex["y"]) < self.__size and abs(nextHex["z"]) < self.__size:
                        if self.__map.get(HexToTuple(nextHex), "Empty") in self.__canMoveTrough:
                            queue.append(nextHex)

                # Out of cells at current distance       
                if popsLeft == 0:
                    depth -= 1
                    popsLeft = len(queue)
            else:
                possibleMoves.extend(queue)
                break

        # Returns only the possible moves that the tank can move to
        result = []
        for moveIndex in range(1, len(possibleMoves)):
            moveTuple = HexToTuple(possibleMoves[moveIndex])
            objectAtMove = self.__map.get(moveTuple, "Empty")
            if not moveTuple in self.__tankMap:
                if objectAtMove in self.__canMoveTo or objectAtMove == tankId:
                    result.append(possibleMoves[moveIndex])

        return result
    
    def move(self, tankId : str, hex : jsonDict) -> None:
        '''
        Moves a given tank to a given hex cell

        :param tankId: Id of the tank to get moves for.
        :param hex: Hex cell to move the tank to
        '''
        # Draw an empty cell.
        self.__tankMap.pop(HexToTuple(self.__tanks[tankId]["position"]))

        cubicCoordinates = HexToTuple(self.__tanks[tankId]["position"])
        leavingCellFill = 'green' if axial_distance(0, 0, cubicCoordinates[0], cubicCoordinates[1]) < 2 else 'white'
        offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=leavingCellFill)
        # Draw an occupied cell.
        cubicCoordinates = HexToTuple(hex)
        offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=self.__teamColors[(int(tankId) - 1) // 5])

        self.__tankMap[HexToTuple(hex)] = tankId
        self.__tanks[tankId]["position"] = hex


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

                cubicCoordinates = tankPosition
                offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
                self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=self.__teamColors[(int(tankId) - 1) // 5])


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
                # Draw an empty cell.
                cubicCoordinates = HexToTuple(self.__tanks[tankId]["position"])
                leavingCellFill = 'green' if axial_distance(0, 0, cubicCoordinates[0], cubicCoordinates[1]) < 2 else 'white'
                offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
                self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=leavingCellFill)
                # Draw an occupied cell.
                cubicCoordinates = HexToTuple(serverTankPosition)
                offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
                self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=self.__teamColors[(int(tankId) - 1) // 5])
                # Update local tank position.
                self.__map.pop(HexToTuple(localTankPosition)) 
                self.__tanks[tankId]["position"] = serverTankPosition
                self.__map[HexToTuple(serverTankPosition)] = tankId