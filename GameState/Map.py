jsonDict = dict[str, any] # alias

class Map():
    def __init__(self, map : jsonDict) -> None:
        '''
        Initializes a map object with the data provided by the game server.

        :param map: A dictionary containing the map data, including its size, name, spawn points and content.
        '''
        self.__size = map["size"]
        self.__name = map["name"]
        self.__spawnPoints = map["spawn_points"]
        self.__initializeBase(map["content"]["base"])


    def __initializeBase(self, base : jsonDict) -> None:
        '''
        Initializes a lookup table of base hex cells to speed up isBase lookups.

        :param base: A dictionary containing the base data for the map.
        '''
        self.__base = {}

        for hex in base:
            self.__base[(hex["x"], hex["y"], hex["z"])] = True


    def isBase(self, hex : jsonDict) -> bool:
        '''
        Determines whether a given hex cell is part of a base on the map.

        :param hex: A dictionary containing the coordinates of the hex cell to check.

        :return: True if the hex cell is part of a base, False otherwise.
        '''
        if (hex["x"], hex["y"], hex["z"]) in self.__base:
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


