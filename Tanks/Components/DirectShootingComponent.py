from dataclasses import dataclass

@dataclass
class DirectShootingComponent:
    """
    Component for handling direct ranged attack information of an entity.

    Attributes:
        maxAttackDistance: The maximum distance at which the attack can be made.
        damage: The amount of damage dealt by the attack.
        rangeBonusEnabled: Indicates whether the attack distance is modified with a range bonus.
    """
    maxAttackDistance: int
    damage: int
    rangeBonusEnabled: bool
