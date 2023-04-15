class DirectShootingComponent:
    """
    Component for handling direct ranged attack information of an entity.
    """

    __slots__ = ("__maxAttackDistance", "__damage")

    def __init__(self, maxAttackDistance: int, damage: int) -> None:
        """
        Initializes a new instance of the DirectShootingComponent class.

        :param maxAttackDistance: The maximum distance at which the attack can be made.
        :param damage: The damage dealt by the attack.
        """
        self.__damage = damage
        self.__maxAttackDistance = maxAttackDistance
    
    def getDamage(self) -> int:
        """
        Returns the damage dealt by the attack.

        :return: An integer representing the damage dealt.
        """
        return self.__damage
    
    def getAttackDistance(self) -> int:
        """
        Returns the maximum distance at which the attack can be made.

        :return: An integer representing the maximum attack distance.
        """
        return self.__maxAttackDistance