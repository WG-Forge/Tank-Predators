from Aliases import jsonDict
from Aliases import positionTuple
from Utils import HexToTuple

class Map:
    def __init__(self, mapData: jsonDict) -> None:
        '''
        Initializes the map object with the given map data.

        :param mapData: A dictionary containing the map data.
        '''
        self.__size = mapData["size"]
        self.__name = mapData["name"]
        self.__map = {}
        self.__initializeMapContent(mapData["content"])

    def __initializeMapContent(self, mapContent: jsonDict) -> None:
        '''
        Initializes the map content.

        :param base: A dictionary containing the map content for the map.
        '''
        for baseHex in mapContent["base"]:
            self.__map[HexToTuple(baseHex)] = "Base"

        for obstacleHex in mapContent["obstacle"]:
            self.__map[HexToTuple(obstacleHex)] = "Obstacle"

    def getSize(self) -> int:
        '''
        Returns the size of the map.

        :return: An integer representing the size of the map.
        '''

        return self.__size
    
    def getName(self) -> str:
        '''
        Returns the name of the map.

        :return: A string representing the name of the map.
        '''
        return self.__name
    
    def objectAt(self, position: positionTuple) -> str:
        '''
        Returns the name of the object located at the given position.

        :param position: A tuple representing the position to look up.
        :return: A string value indicating the name of the object located at the given position. 
                 If no object exists at the given position, returns "Empty".
        '''
        return self.__map.get(position, "Empty")

    def __iter__(self):
        """
        Returns an iterator over the positions and objects in the Map.
        """
        for position, obj in self.__map.items():
            yield position, obj