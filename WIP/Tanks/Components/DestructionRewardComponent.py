from dataclasses import dataclass

@dataclass
class DestructionRewardComponent:
    """
    A component representing the destruction reward of an entity.

    Attributes:
        destructionReward: The amount of reward given upon destruction of the entity.
    """
    destructionReward: int
