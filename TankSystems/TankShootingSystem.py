from Events.Events import TankAddedEvent
from Events.Events import TankMovedEvent
from Events.Events import TankShotEvent
from Events.Events import TankDestroyedEvent
from Events.Events import TankRespawnedEvent
from Events.Events import TankRangeBonusEvent
from Events.EventManager import EventManager
from Tanks.Tank import Tank
from Map import Map
from Tanks.Components.DirectShootingComponent import DirectShootingComponent
from Tanks.Components.CurvedShootingComponent import CurvedShootingComponent
from Aliases import positionTuple, jsonDict
import itertools
from Utils import HexToTuple
import logging

class TankShootingSystem:
    """
    A system that manages the shooting of tanks.
    """
    def __init__(self, map: Map, eventManager: EventManager, attackMatrix: jsonDict, catapultUsage: list):
        """
        Initializes the TankShootingSystem.

        :param map: An instance of the Map that holds static game information.
        :param eventManager: The EventManager instance to use for triggering events.
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
        self.__canShootTrough = {"Empty", "Base", "Catapult", "LightRepair", "HardRepair"}
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__attackMatrix = {int(key) : values for key, values in attackMatrix.items()}
        self.__catapultUsage = self.__calculateCatapultUsage(catapultUsage)

    def __calculateCatapultUsage(self, catapultUsage: list) -> dict:
        """
        Calculates the usage of each catapult position based on the provided list.

        :param catapultUsage: A history of catapult usage. Catapults can be used a limited number of times.
        :return: A dictionary where the keys are hex positions and the values are the number of times the catapult at that position was used.
        """
        usage = {}

        for hex in catapultUsage:
            position = HexToTuple(hex)
            if position not in usage:
                usage[position] = 1
            else:
                usage[position] += 1

        return usage

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
                logging.debug(f"Catapult used: TankId:{tankId}, Position:{tankPosition}, TotalUses:{self.__catapultUsage[tankPosition]}")
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

    def getShootingOptions(self, tankId: str) -> list[tuple[positionTuple,list[str]]]:
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
        return (abs(position1[0] - position2[0]) + abs(position1[1] - position2[1]) + abs(position1[2] - position2[2])) // 2
    
    def __getCurvedShootingOptions(self, shooterTankId: str) -> list[tuple[positionTuple,list[str]]]:
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
    
    def __getDirectShootingTargets(self, shooterTankId, ownerId, startingPosition, targetPermutation, maxAttackDistance) -> list[str]:
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

    def __getDirectShootingOptions(self, shooterTankId: str) -> list[tuple[positionTuple,list[str]]]:
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
            shootingOptions.append((shootingDirection, self.__getDirectShootingTargets(shooterTankId, shooterOwnerId, shooterPosition, permutation, shootingComponent.maxAttackDistance)))

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
                if shootingComponent.minAttackRange > self.__distance(targetPosition , shooterPosition) > shootingComponent.maxAttackRange:
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

                targets = self.__getDirectShootingTargets(shooterId, shooterOwnerId, shooterPosition, permutation, shootingComponent.maxAttackDistance)
            else:
                raise KeyError(f"Unknown shooting component {type(shootingComponent).__name__} for TankId:{shooterId}")
            
            for targetId in targets:
                targetOwnerId = self.__tanks[targetId]["owner"]
                if not targetOwnerId in self.__attackMatrix[shooterOwnerId]:
                    self.__attackMatrix[shooterOwnerId].append(targetOwnerId)
                self.__eventManager.triggerEvent(TankShotEvent, targetId, shootingComponent.damage)

            if shootingComponent.rangeBonusEnabled:
                self.__removeBonusRange(shootingComponent)

    def turn(self, ownerId):
        self.__attackMatrix[ownerId].clear()

    def test(self, attackMatrixServer):
        for key, valueList in attackMatrixServer.items():
            for value in self.__attackMatrix[int(key)]:
                if value not in valueList:
                    logging.error("ATTACK MATRIX MISSMATCH")
                    logging.error("LOCAL:")
                    logging.error(self.__attackMatrix)
                    logging.error("SERVER:")
                    logging.error(attackMatrixServer)
                    return