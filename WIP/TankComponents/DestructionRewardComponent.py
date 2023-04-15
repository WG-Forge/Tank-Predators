class DestructionRewardComponent:
    """
    Component for storing the destruction reward of an entity.
    """

    __slots__ = ("__destructionReward",)

    def __init__(self, destructionReward: int) -> None:
        """
        Initializes a new instance of the DestructionRewardComponent class.

        :param destructionReward: The destruction reward of the entity.
        """
        self.__destructionReward = destructionReward

    def getDestructionReward(self) -> int:
        """
        Returns the destruction reward of the entity.

        :return: An integer representing the destruction reward of the entity.
        """
        return self.__destructionReward
