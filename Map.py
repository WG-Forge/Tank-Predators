import itertools
from Tanks import *
from Utils import HexToTuple

jsonDict = dict[str, any] # alias
from HexGrid import *
from tkinter import *

class Map():
    def __init__(self, map : jsonDict, gameState : jsonDict) -> None:
        '''
        Initializes a map object with the data provided by the game server.

        :param map: A dictionary containing the map data, including its size, name, spawn points and content.
        '''
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__canMoveTo = ["Empty", "Base"]
        self.__canMoveTrough = ["Empty", "Base"]

        self.__size = map["size"]
        self.__name = map["name"]
        self.__spawnPoints = map["spawn_points"]
        self.__initializeBase(map["content"]["base"])
        self.__initializeTanks(gameState["vehicles"])
        self.__formPlayerColors(gameState["players"])
        self.__drawMap()

    def __initializeBase(self, base : jsonDict) -> None:
        '''
        Initializes a lookup table of base hex cells to speed up isBase lookups.

        :param base: A dictionary containing the base data for the map.
        '''
        self.__map = {}

        for hex in base:
            self.__map[HexToTuple(hex)] = "Base"


    def __initializeTanks(self, vehicles : jsonDict) -> None:
        self.__tanks = vehicles
        
        for id, tank in self.__tanks.items():
            self.__canMoveTrough.append(id)
            self.__map[HexToTuple(tank["position"])] = id

    def __formPlayerColors(self, players: list) -> None:
        '''
        Forms the colors which are used to respresent different teams.
        '''
        self.__teamColors = {}
        colors = ["orange", "purple", "blue"]
        for index, player in enumerate(players):
            self.__teamColors[player["idx"]] = colors[index]

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

        # draw spawn points
        spawnColors = ['orange', 'purple', 'blue']
        for index, playerSpawnPoints in enumerate(self.__spawnPoints):
            cellFill = spawnColors[index]
            for spawnPoint in playerSpawnPoints.values():
                cubicCoordinates = HexToTuple(spawnPoint[0])
                offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
                self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=cellFill)


    def isBase(self, hex : jsonDict) -> bool:
        '''
        Determines whether a given hex cell is part of a base on the map.

        :param hex: A dictionary containing the coordinates of the hex cell to check.

        :return: True if the hex cell is part of a base, False otherwise.
        '''
        if self.__map.get(HexToTuple(hex), "Empty") == "Base":
            return True
        
        return False
    
    def getSpawnPoints(self, playerIndex : int, tankClass : str) -> jsonDict:
        '''
        Retrieves the spawn points for a player's tank of a specified class.

        :param playerIndex: The index of the player whose spawn points should be retrieved.
        :param tankClass: The class of tank for which to retrieve spawn points.

        :return: A dictionary containing the spawn points for the specified tank class.
        '''
        return self.__spawnPoints[playerIndex][tankClass]

    def getMoves(self, tankId : str) -> jsonDict:
        tank = Tanks.allTanks[self.__tanks[tankId]["vehicle_type"]]
        depth = tank["sp"]

        queue = []
        queue.append(self.__tanks[tankId]["position"])
        popsLeft = 1
        possibleMoves = []

        while len(queue) > 0:
            currentHex = queue.pop(0)
            popsLeft -= 1
            possibleMoves.append(currentHex)

            if depth > 0:
                for permutation in self.__hexPermutations:
                    nextHex = {}
                    nextHex["x"] = currentHex["x"] + permutation[0]
                    nextHex["y"] = currentHex["y"] + permutation[1]
                    nextHex["z"] = currentHex["z"] + permutation[2]

                    if not nextHex in possibleMoves and not nextHex in queue and abs(nextHex["x"]) < self.__size and abs(nextHex["y"]) < self.__size and abs(nextHex["z"]) < self.__size:
                        if self.__map.get(HexToTuple(nextHex), "Empty") in self.__canMoveTrough:
                            queue.append(nextHex)
                        
                if popsLeft == 0:
                    depth -= 1
                    popsLeft = len(queue)
                else:
                    possibleMoves.extend(queue)
                    break

        return [move for move in possibleMoves if self.__map.get(HexToTuple(move), "Empty") in self.__canMoveTo]
    
    def move(self, tankId : str, hex : jsonDict) -> None:
        self.__map.pop(HexToTuple(self.__tanks[tankId]["position"]))

        # Draw an empty cell.
        cubicCoordinates = HexToTuple(self.__tanks[tankId]["position"])
        offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill="white")
        # Draw an occupied cell.
        cubicCoordinates = HexToTuple(hex)
        offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
        self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=self.__teamColors[self.__tanks[tankId]["player_id"]])

        self.__tanks[tankId]["position"] = hex
        self.__map[HexToTuple(self.__tanks[tankId]["position"])] = tankId

    def showMap(self) -> None:
        '''
        Shows the window on which the map is presented.
        '''
        self.__window.mainloop()
    
    def updateMap(self, gameState: jsonDict) -> None:
        '''
        Updates the map, i.e. checks whether there are any differences between local and server gamestate.
        '''
        for tankId, tankInfo in self.__tanks.items():
            localTankPosition = tankInfo["position"]
            serverTankPosition = gameState["vehicles"][tankId]["position"]
            if HexToTuple(localTankPosition) != HexToTuple(serverTankPosition):
                # Draw an empty cell.
                cubicCoordinates = HexToTuple(localTankPosition)
                offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
                self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill="white")
                # Draw an occupied cell.
                cubicCoordinates = HexToTuple(serverTankPosition)
                offsetCoordinates = cube_to_offset(cubicCoordinates[0], cubicCoordinates[1])
                self.__grid.setCell(offsetCoordinates[0] + self.__size - 1, offsetCoordinates[1] + self.__size - 1, fill=self.__teamColors[tankInfo["player_id"]])
                # Update local tank position.
                self.__tanks[tankId]["position"] = serverTankPosition
