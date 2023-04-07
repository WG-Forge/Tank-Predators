import itertools
from Tanks import *
from Utils import HexToTuple
from typing import List

jsonDict = dict[str, any] # alias

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

        self.__size = map["size"]
        self.__name = map["name"]
        self.__initializeSpawnPoints(map["spawn_points"])
        self.__initializeBase(map["content"]["base"])
        self.__initializeTanks(gameState["vehicles"])


    def __initializeSpawnPoints(self, allPlayerSpawnPoints : jsonDict) -> None:
        '''
        Initializes the spawn points on the map.

        :param allPlayerSpawnPoints: A dictionary containing the spawn points for all players.
        '''
        self.__spawnPoints = {}

        for spawnPoints in allPlayerSpawnPoints:
            for tankName, tankSpawnPoints in spawnPoints.items():
                for tankSpawnPoint in tankSpawnPoints:
                    self.__spawnPoints[HexToTuple(tankSpawnPoint)] = tankName


    def __initializeBase(self, base : jsonDict) -> None:
        '''
        Initializes the base on the map.

        :param base: A dictionary containing the base data for the map.
        '''
        self.__map = {}

        for hex in base:
            self.__map[HexToTuple(hex)] = "Base"


    def __initializeTanks(self, vehicles : jsonDict) -> None:
        '''
        Initializes the tanks on the map.

        :param vehicles: A dictionary containing the vehicle data for the map.
        '''
        self.__tanks = vehicles
        
        for id, tank in self.__tanks.items():
            self.__canMoveTrough.append(id)
            self.__map[HexToTuple(tank["position"])] = id


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
        for move in possibleMoves:
            moveTuple = HexToTuple(move)
            isSpawnPoint = self.__spawnPoints.get(moveTuple, None)
            if not isSpawnPoint or (isSpawnPoint and self.__tanks[tankId]["spawn_position"] == move):
                if self.__map.get(moveTuple, "Empty") in self.__canMoveTo:
                    result.append(move)

        return result
    
    def move(self, tankId : str, hex : jsonDict) -> None:
        '''
        Moves a given tank to a given hex cell

        :param tankId: Id of the tank to get moves for.
        :param hex: Hex cell to move the tank to
        '''
        self.__map.pop(HexToTuple(self.__tanks[tankId]["position"]))
        self.__tanks[tankId]["position"] = hex
        self.__map[HexToTuple(self.__tanks[tankId]["position"])] = tankId
