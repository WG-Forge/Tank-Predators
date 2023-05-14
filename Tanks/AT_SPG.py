from Tanks.Components.DirectShootingComponent import DirectShootingComponent
from Tanks.Tank import Tank
from Aliases import jsonDict, shootingOptionsList
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

    def getBestTarget(self, shootingOptions: shootingOptionsList, tanks):
        shootingOptionsInfo = dict()
        allyTankDamage = self.getComponent("shooting").damage

        for shootingPosition, enemyTankIds in shootingOptions:
            destroyableTanks = 0
            capturePoints = 0
            for enemyTankId in enemyTankIds:
                enemyTank = tanks[enemyTankId]
                enemyTankHealth = enemyTank.getComponent("health").currentHealth
                if enemyTankHealth <= allyTankDamage:
                    destroyableTanks += 1
                capturePoints += enemyTank.getComponent("capture").capturePoints

            shootingOptionsInfo[shootingPosition] = {
                'destroyable': destroyableTanks,
                'capturePoints': capturePoints,
                'numberOfTanks': len(enemyTankIds)
            }
        # Num destroyable > num attacking > num capture points
        shootingPositions = [k for k, v in sorted(shootingOptionsInfo.items(),
                                                  key=lambda x: (-x[1]["destroyable"], -x[1]["numberOfTanks"],
                                                                 -x[1]["capturePoints"]))]
        return shootingPositions[0]