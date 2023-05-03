from Events.Events import TankAddedEvent
from Events.Events import TankMovedEvent
from Events.Events import TankShotEvent
from Events.Events import TankDestroyedEvent
from Events.Events import TankRespawnedEvent
from Events.Events import TankRangeBonusEvent
from Events.EventManager import EventManager
from Tanks.Tank import Tank
from TankManagement.TankManager import TankManager
from Map import Map
from Tanks.Components.DirectShootingComponent import DirectShootingComponent
from Tanks.Components.CurvedShootingComponent import CurvedShootingComponent
from Tanks.Components.HealthComponent import HealthComponent
from Aliases import positionTuple, jsonDict, shootingOptionsList
import itertools
from Utils import HexToTuple
from Constants import ShootingModifier
import logging


class TankShootingSystem:
    """
    A system that manages the shooting of tanks.
    """

    def __init__(self, map: Map, eventManager: EventManager,
                 pathingOffsets: list[dict[tuple[int, int, int], set[tuple[int, int, int]]]], attackMatrix: jsonDict,
                 catapultUsage: list, tankManager: TankManager):
        """
        Initializes the TankShootingSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
        :param pathingOffsets: A list of dictionaries representing all possible positions a target can move to in a given number of steps 
        """
        self.__map = map
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__eventManager.addHandler(TankMovedEvent, self.onTankMoved)
        self.__eventManager.addHandler(TankDestroyedEvent, self.onTankDestroyed)
        self.__eventManager.addHandler(TankRespawnedEvent, self.onTankRespawned)
        self.__eventManager.addHandler(TankRangeBonusEvent, self.onRangeBonusReceived)
        self.__tanks = {}
        self.__tankMap = {}
        self.__tankManager = tankManager
        self.__canShootTrough = {"Empty", "Base", "Catapult", "LightRepair", "HardRepair"}
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__initializeAttackMatrix(attackMatrix)
        self.__initializeCatapultUsage(catapultUsage)
        self.__pathingOffsets = pathingOffsets

    def __initializeAttackMatrix(self, attackMatrix: jsonDict):
        self.__attackMatrix = {int(key) : values for key, values in attackMatrix.items()}

    def __initializeCatapultUsage(self, catapultUsage: list) -> dict:
        """
        Initializes the usage of each catapult position based on the provided list.

        :param catapultUsage: A history of catapult usage. Catapults can be used a limited number of times.
        """
        self.__catapultUsage = {}

        for hex in catapultUsage:
            position = HexToTuple(hex)
            if position not in self.__catapultUsage:
                self.__catapultUsage[position] = 1
            else:
                self.__catapultUsage[position] += 1

    def onRangeBonusReceived(self, tankId: str):
        tank = self.__tanks.get(tankId)

        if tank:
            shootingComponent = tank["shooting"]
            tankPosition = tank["position"]

            if not shootingComponent.rangeBonusEnabled:
                catapultUsage = self.__catapultUsage.get(tankPosition, 0)
                if catapultUsage == 0:
                    self.__catapultUsage[tankPosition] = 1
                elif catapultUsage >= 3:
                    return
                else:
                    self.__catapultUsage[tankPosition] += 1
                logging.debug(
                    f"Catapult used: TankId:{tankId}, Position:{tankPosition}, TotalUses:{self.__catapultUsage[tankPosition]}")
                self.__addBonusRange(shootingComponent)

    def __addBonusRange(self, shootingComponent):
        if isinstance(shootingComponent, CurvedShootingComponent):
            shootingComponent.rangeBonusEnabled = True
            shootingComponent.maxAttackRange += 1
        elif isinstance(shootingComponent, DirectShootingComponent):
            shootingComponent.rangeBonusEnabled = True
            shootingComponent.maxAttackDistance += 1

    def __removeBonusRange(self, shootingComponent):
        if isinstance(shootingComponent, CurvedShootingComponent):
            shootingComponent.rangeBonusEnabled = False
            shootingComponent.maxAttackRange -= 1
        elif isinstance(shootingComponent, DirectShootingComponent):
            shootingComponent.rangeBonusEnabled = False
            shootingComponent.maxAttackDistance -= 1

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has shooting, owner and position components

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        shootingComponent = tankEntity.getComponent("shooting")
        positionComponent = tankEntity.getComponent("position")
        ownerComponent = tankEntity.getComponent("owner")

        if shootingComponent and positionComponent and ownerComponent:
            self.__tanks[tankId] = {
                "shooting": shootingComponent,
                "position": positionComponent.position,
                "owner": ownerComponent.ownerId,
                "isAlive": True,
            }

            self.__tankMap[positionComponent.position] = tankId

            if not ownerComponent.ownerId in self.__attackMatrix:
                self.__attackMatrix[ownerComponent.ownerId] = []

            if shootingComponent.rangeBonusEnabled:
                self.__addBonusRange(shootingComponent)

    def onTankMoved(self, tankId: str, newPosition: positionTuple) -> None:
        """
        Event handler. Handles updating tank positions in this system.

        :param tankId: The ID of the tank that got moved.
        :param newPosition: New position of the tank.
        """
        if tankId in self.__tanks:
            self.__tankMap.pop(self.__tanks[tankId]["position"])
            self.__tanks[tankId]["position"] = newPosition
            self.__tankMap[newPosition] = tankId

    def onTankDestroyed(self, tankId: str) -> None:
        """
        Event handler. Handles destruction of the tank.

        :param tankId: The ID of the tank that got destroyed.
        """
        if tankId in self.__tanks:
            self.__tanks[tankId]["isAlive"] = False

    def onTankRespawned(self, tankId: str) -> None:
        """
        Event handler. Handles respawning of the tank.

        :param tankId: The ID of the tank that got respawned.
        """
        if tankId in self.__tanks:
            self.__tanks[tankId]["isAlive"] = True

    def getShootingOptions(self, tankId: str) -> shootingOptionsList:
        """
        Returns a list of shooting options for the specified tank.

        :param tankId: The ID of the tank for which to get the shooting options.
        :return: A list of shooting options, where each option is represented as a tuple, 
            containing the target position and a list of tank IDs that can be hit by shooting at that position.
        :raises ValueError: If the specified tank ID is not in the shooting system.
        :raises KeyError: If the shooting component of the specified tank is not recognized.
        """
        tank = self.__tanks.get(tankId)

        if tank is None:
            raise ValueError(f"TankId:{tankId} is not in the shooting system")

        shootingComponent = tank["shooting"]

        if isinstance(shootingComponent, CurvedShootingComponent):
            return self.__getCurvedShootingOptions(tankId)
        elif isinstance(shootingComponent, DirectShootingComponent):
            return self.__getDirectShootingOptions(tankId)
        else:
            raise KeyError(f"Unknown shooting component {type(shootingComponent).__name__} for TankId:{tankId}")

    def __canAttack(self, shooterTankId: str, shooterOwnerId: int, receiverTankId, receiverOwnerId: int):
        if shooterOwnerId == receiverOwnerId or not self.__tanks[receiverTankId]["isAlive"]:
            return False

        attackParticipants = [shooterOwnerId, receiverOwnerId]
        otherOwnerIds = [key for key in self.__attackMatrix.keys() if key not in attackParticipants]

        if shooterOwnerId in self.__attackMatrix[receiverOwnerId]:
            return True

        for otherOwnerId in otherOwnerIds:
            if receiverOwnerId in self.__attackMatrix[otherOwnerId]:
                return False

        return True

    def __distance(self, position1: positionTuple, position2: positionTuple) -> int:
        """
        Returns the distance between two positions.

        :param position1: The first position.
        :param position2: The second position.
        :return: The distance between the two positions.
        """
        return (abs(position1[0] - position2[0]) + abs(position1[1] - position2[1]) + abs(
            position1[2] - position2[2])) // 2

    def __getCurvedShootingOptions(self, shooterTankId: str) -> shootingOptionsList:
        """
        Returns a list of curved shooting options for the specified tank.

        :param shooterTankId: The ID of the tank for which to get the shooting options.
        :return: A list of shooting options, where each option is represented as a tuple,
            containing the target position and a list of tank IDs that can be hit by shooting at that position.
        """
        shootingOptions = []

        shooterOwnerId = self.__tanks[shooterTankId]["owner"]
        shooterPosition = self.__tanks[shooterTankId]["position"]
        shootingComponent = self.__tanks[shooterTankId]["shooting"]

        for tankId, tankComponents in self.__tanks.items():
            if not (self.__canAttack(shooterTankId, shooterOwnerId, tankId, tankComponents["owner"])):
                continue
            targetPosition = tankComponents["position"]
            distance = self.__distance(shooterPosition, targetPosition)

            if shootingComponent.minAttackRange <= distance <= shootingComponent.maxAttackRange:
                shootingOptions.append((targetPosition, [tankId]))

        return shootingOptions

    def __getDirectShootingTargets(self, shooterTankId, ownerId, startingPosition, targetPermutation,
                                   maxAttackDistance) -> list[str]:
        """
        Returns a list of tank IDs that can be hit by direct shooting.

        :param shooterTankId: The tank ID of the tank that is doing the shooting.
        :param ownerId: The owner ID of the tank that is doing the shooting.
        :param startingPosition: The starting position of the shooter tank.
        :param targetPermutation: The direction of the shooting.
        :param maxAttackDistance: The maximum distance that can be reached by the shooter tank.
        :return: A list of tank IDs that can be hit by direct shooting.
        """
        targets = []

        for distance in range(1, maxAttackDistance + 1):
            currentPosition = tuple(x + y * distance for x, y in zip(startingPosition, targetPermutation))
            if self.__map.objectAt(currentPosition) in self.__canShootTrough:
                targetTankId = self.__tankMap.get(currentPosition)

                if not targetTankId:
                    continue

                if self.__canAttack(shooterTankId, ownerId, targetTankId, self.__tanks[targetTankId]["owner"]):
                    targets.append(targetTankId)
            else:
                break

        return targets

    def __getDirectShootingOptions(self, shooterTankId: str) -> shootingOptionsList:
        """
        Returns a list of direct shooting options for the specified tank.

        :param shooterTankId: The ID of the tank for which to get the shooting options.
        :return: A list of shooting options, where each option is represented as a tuple,
            containing the target position and a list of tank IDs that can be hit by shooting at that position.
        """
        shootingOptions = []

        shooterOwnerId = self.__tanks[shooterTankId]["owner"]
        shooterPosition = self.__tanks[shooterTankId]["position"]
        shootingComponent = self.__tanks[shooterTankId]["shooting"]

        for permutation in self.__hexPermutations:
            shootingDirection = tuple(x + y for x, y in zip(shooterPosition, permutation))
            shootingOptions.append((shootingDirection,
                                    self.__getDirectShootingTargets(shooterTankId, shooterOwnerId, shooterPosition,
                                                                    permutation, shootingComponent.maxAttackDistance)))

        return [shootingOption for shootingOption in shootingOptions if len(shootingOption[1])]

    def shoot(self, shooterId: str, targetPosition: positionTuple) -> None:
        """
        Handles shooting from a tank to a target position.

        :param shooterId: The ID of the tank that shoots.
        :param targetPosition: The position tuple of the target.
        """
        shooter = self.__tanks.get(shooterId)
        if shooter:
            shootingComponent = shooter["shooting"]
            shooterPosition = shooter["position"]
            shooterOwnerId = shooter["owner"]

            if isinstance(shootingComponent, CurvedShootingComponent):
                targets = []
                if not targetPosition in self.__tankMap:
                    pass
                if shootingComponent.minAttackRange > self.__distance(targetPosition,
                                                                      shooterPosition) > shootingComponent.maxAttackRange:
                    pass

                targetId = self.__tankMap[targetPosition]
                target = self.__tanks[targetId]
                if shooterOwnerId != target["owner"]:
                    targets.append(targetId)
            elif isinstance(shootingComponent, DirectShootingComponent):
                targets = []
                permutation = tuple(x - y for x, y in zip(targetPosition, shooterPosition))

                if not permutation in self.__hexPermutations:
                    pass

                targets = self.__getDirectShootingTargets(shooterId, shooterOwnerId, shooterPosition, permutation,
                                                          shootingComponent.maxAttackDistance)
            else:
                raise KeyError(f"Unknown shooting component {type(shootingComponent).__name__} for TankId:{shooterId}")

            for targetId in targets:
                targetOwnerId = self.__tanks[targetId]["owner"]
                if not targetOwnerId in self.__attackMatrix[shooterOwnerId]:
                    self.__attackMatrix[shooterOwnerId].append(targetOwnerId)
                self.__eventManager.triggerEvent(TankShotEvent, targetId, shootingComponent.damage)

            if shootingComponent.rangeBonusEnabled:
                self.__removeBonusRange(shootingComponent)

    def getShootablePositions(self, tankId: str) -> set[positionTuple]:
        """
        Returns a set of shootable positions for the specified tank.

        :param tankId: The ID of the tank for which to get the shooting shootable positions.
        :return: A set of shootable positions, where each option is represented as a position tuple, 
        :raises ValueError: If the specified tank ID is not in the shooting system.
        :raises KeyError: If the shooting component of the specified tank is not recognized.
        """
        tank = self.__tanks.get(tankId)

        if tank is None:
            raise ValueError(f"TankId:{tankId} is not in the shooting system")

        shootingComponent = tank["shooting"]

        if isinstance(shootingComponent, CurvedShootingComponent):
            return self.__getCurvedShootablePositions(tankId)
        elif isinstance(shootingComponent, DirectShootingComponent):
            return self.__getDirectShootablePositions(tankId)
        else:
            raise KeyError(f"Unknown shooting component {type(shootingComponent).__name__} for TankId:{tankId}")

    def __getCurvedShootablePositions(self, shooterTankId: str) -> set[positionTuple]:
        """
        Returns a set of curved shootable positions for the specified tank.

        :param shooterTankId: The ID of the tank for which to get the shooting options.
        :return: A set of shooting options, where each option is represented as a position tuple
        """
        shootingOptions = set()
        shooterPosition = self.__tanks[shooterTankId]["position"]
        shootingComponent = self.__tanks[shooterTankId]["shooting"]

        for distance in range(shootingComponent.minAttackRange, shootingComponent.maxAttackRange + 1):
            for offset in self.__pathingOffsets[distance]:
                shootingOptions.add(tuple(x + y for x, y in zip(shooterPosition, offset)))

        return shootingOptions

    def __getDirectShootablePositions(self, shooterTankId: str) -> set[positionTuple]:
        """
        Returns a set of direct shootable positions for the specified tank.

        :param shooterTankId: The ID of the tank for which to get the shooting options.
        :return: A set of shooting options, where each option is represented as a position tuple
        """
        shootingOptions = set()
        shooterPosition = self.__tanks[shooterTankId]["position"]
        shootingComponent = self.__tanks[shooterTankId]["shooting"]

        for permutation in self.__hexPermutations:
            for distance in range(1, shootingComponent.maxAttackDistance + 1):
                shootingPosition = tuple(x + y * distance for x, y in zip(shooterPosition, permutation))
                if self.__map.objectAt(shooterPosition) in self.__canShootTrough:
                    shootingOptions.add(shootingPosition)
                else:
                    break

        return shootingOptions
    
    def turn(self, ownerId):
        self.__attackMatrix[ownerId].clear()

    def reset(self, attackMatrix: jsonDict, catapultUsage: list):
        self.__initializeAttackMatrix(attackMatrix)
        self.__initializeCatapultUsage(catapultUsage)
        self.__tankMap.clear()
        self.__tanks.clear()

    def getBestTarget(self, tankID: str, shootingOptions: shootingOptionsList) -> tuple[positionTuple, int]:
        """
        Determines best possible target to shoot, depending on current game state.
        The bigger the final modifier values is, the greater is the benefit of shooting at the target
        Target with modifiers below zero should not be considered for shooting

        :param: tankID of tank that shoots
        :param: shootingOptions shootingOptionsList of all possible targets
        :return: tuple of positionTuple(tile at which we should fire) and int final modifier value
        """
        numOptions = len(shootingOptions)
        allyTank = self.__tankManager.getTank(tankID)
        if numOptions == 0:
            return (-1, -1, -1), -1  # -1 because there are no possible options

        modifiers = [0 for _ in range(numOptions)]
        for i in range(numOptions):
            numberOfTargets = len(shootingOptions[i][1])
            # number of targets we will shoot
            modifiers[i] += ShootingModifier.NUMBER_OF_TARGETS * numberOfTargets
            # turns left
            for j in range(numberOfTargets):
                targetTank = self.__tankManager.getTank(shootingOptions[i][1][j])
                # target is at central base
                if self.__map.objectAt(shootingOptions[i][0]) == "Base":
                    modifiers[i] += ShootingModifier.TANK_ON_CENTRAL_BASE
                # checking target health
                targetHealth = targetTank.getComponent("health").currentHealth
                allyDamage = allyTank.getComponent("shooting").damage
                if allyDamage >= targetHealth:
                    modifiers[i] += ShootingModifier.ENOUGH_TO_DESTROY

        maxModifier = modifiers[0]
        maxTuple = shootingOptions[0][0]
        for i in range(1, numOptions):
            if modifiers[i] > maxModifier:
                maxModifier = modifiers[i]
                maxTuple = shootingOptions[i][0]

        return maxTuple, maxModifier
