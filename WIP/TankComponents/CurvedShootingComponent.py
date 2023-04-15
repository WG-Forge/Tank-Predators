from Aliases import rangeTuple

class CurvedShootingComponent:
    """
    Component for handling curved ranged attack information of an entity.
    """

    __slots__ = ("__minAttackRange", "__maxAttackRange", "__damage")

    def __init__(self, minAttackRange: int, maxAttackRange: int, damage: int) -> None:
        """
        Initializes a new instance of the CurvedShootingComponent class.

        :param minAttackRange: The minimum attack range.
        :param maxAttackRange: The maximum attack range.
        :damage: The damage dealt by the attack.
        """
        self.__damage = damage
        self.__minAttackRange = minAttackRange
        self.__maxAttackRange = maxAttackRange
    
    def getDamage(self) -> int:
        """
        Returns the damage dealt by the attack.

        :return: An integer representing the damage dealt.
        """
        return self.__damage
    
    def getRange(self) -> rangeTuple:
        """
        Returns the minimum and maximum attack ranges.
        
        :return: A tuple containing the minimum and maximum attack ranges.
        """
        return (self.__minAttackRange, self.__maxAttackRange)