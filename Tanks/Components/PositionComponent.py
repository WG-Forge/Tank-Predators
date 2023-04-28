from Aliases import positionTuple
from dataclasses import dataclass

@dataclass
class PositionComponent:
    """
    Component for handling the position of an entity.

    Attributes:
        spawnPosition: The spawn position of the entity.
        position: The current position of the entity.
        speed: The speed of the entity, representing the maximum distance it can travel per turn.
    """
    spawnPosition: positionTuple
    position: positionTuple
    speed: int