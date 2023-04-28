from dataclasses import dataclass

@dataclass
class HealthComponent:
    """
    Component for handling the health of an entity.

    Attributes:
        maxHealth: The maximum health value of the entity.
        currentHealth: The current health value of the entity.
    """
    maxHealth: int
    currentHealth: int