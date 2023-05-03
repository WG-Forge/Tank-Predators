from Tanks.Components.DirectShootingComponent import DirectShootingComponent
from Tanks.Tank import Tank
from Aliases import positionTuple
from Aliases import jsonDict
import Tanks.Settings as Settings


class AT_SPG(Tank):
    __slots__ = ()

    def __init__(self, tankData: jsonDict) -> None:
        """
        Initializes a tank destroyer.

        :param tankData: A dictionary containing all the data of the tank entity.
        """
        super().__init__(tankData, Settings.TANKS["AT_SPG"])

    def _initializeShooting(self, settings: jsonDict, shootingRangeBonus: bool) -> None:
        """
        Overrides initialization of the shooting component for the AT-SPG tank.

        :param settings: A dictionary containing the settings of the tank.
            - "maxAttackDistance": An integer representing the maximum attack distance of the direct shot.
            - "damage": An integer representing the damage dealt by the tank's attacks.
        :param rangeBonusEnabled: Indicates whether the attack range bonus is enabled or not.
        """
        self._setComponent("shooting", DirectShootingComponent(settings["maxAttackDistance"], settings["damage"],
                                                               shootingRangeBonus))
