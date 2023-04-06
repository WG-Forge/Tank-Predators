from abc import ABC, abstractmethod  # Abstract base class

jsonDict = dict[str, any] # alias

class Tank(ABC):
    """
    Abstract base class for tanks.
    """
    __slots__ = ("hp", "sp", "damage", "destructionPoints", "position")

    def _setAttributes(self, hp: int, sp: int, damage: int, destructionPoints: int, position: dict[str, any]) -> None:
        """
        Sets the attributes of the tank.

        Arguments:
            :param hp: Health points of the tank.
            :param sp: Speed points of the tank.
            :param damage: Damage it causes on hitting other tank.
            :param destructionPoints: Points awarded for destroying this tank.
            :param position: Position of the tank on the map.
        """
        self.hp = hp
        self.sp = sp
        self.damage = damage
        self.destructionPoints = destructionPoints
        self.position = position


    def moveTo(self, position : jsonDict) -> None:
        '''
        Moves the tank to a given hex cell position

        :param position: Dictionary with new position data
        '''
        self.position = position
