from Aliases import positionTuple

class PositionComponent:
    """
    Component for handling the position of an entity.
    """

    __slots__ = ("__spawnPosition", "__position", "__speed")

    def __init__(self, spawnPosition : positionTuple, position : positionTuple, speed: int) -> None:
        """
        Initializes a new instance of the PositionComponent class.

        :param spawnPosition: The spawn position of the entity.
        :param position: The current position of the entity.
        :param speed: The speed of the entity, representing the maximum distance it can travel per turn.
        """
        self.__spawnPosition = spawnPosition
        self.__position = position
        self.__speed = speed

    def move(self, newPosition : positionTuple) -> None:
        """
        Moves the entity to the specified position.

        :param newPosition: The new position of the entity.
        """
        self.__position = newPosition

    def moveToSpawn(self) -> None:
        """
        Moves the entity to its spawn position.
        """
        self.move(self.__spawnPosition)

    def getPosition(self) -> positionTuple:
        """
        Returns the current position of the entity.

        :return: A tuple containing the x, y, and z coordinates of the entity's position.
        """
        return self.__position
    
    def getSpeed(self) -> int:
        """
        Returns the speed of the entity.

        :return: An integer representing the speed of the entity.
        """
        return self.__speed