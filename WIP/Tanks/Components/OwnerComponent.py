
from dataclasses import dataclass

@dataclass
class OwnerComponent:
    """
    Component for handling the owner of an entity.

    Attributes:
        ownerId: The id of the owner that the entity belongs to.
    """
    ownerId: int
