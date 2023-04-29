from dataclasses import dataclass

@dataclass
class CurvedShootingComponent:
    """
    A component that stores information about a curved ranged attack that an entity can perform.

    Attributes:
        minAttackRange: The minimum attack range of the attack.
        maxAttackRange: The maximum attack range of the attack.
        damage: The amount of damage dealt by the attack.
        rangeBonusEnabled: Indicates whether the attack range is modified with a range bonus.
    """
    minAttackRange: int
    maxAttackRange: int
    damage: int
    rangeBonusEnabled: bool