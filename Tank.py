from abc import ABC, abstractmethod  # Abstract base class


class Tank(ABC):
    """
    Abstract tank class\n
    HP - health points\n
    SP - speed points\n
    Damage - damage it causes on hitting other tank\n
    FireRange - Distance from another tank needed to fire a shot
    """
    __slots__ = ("hp", "sp", "damage", "destructionPoints", "fireRange")
