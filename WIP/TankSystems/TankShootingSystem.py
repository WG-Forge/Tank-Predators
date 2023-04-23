from Events.Events import TankAddedEvent
from Events.Events import TankMovedEvent
from Events.Events import TankShotEvent
from Events.EventManager import EventManager
from Tanks.Tank import Tank
from Map import Map
from Tanks.Components.DirectShootingComponent import DirectShootingComponent
from Tanks.Components.CurvedShootingComponent import CurvedShootingComponent
from Aliases import positionTuple
import itertools

class TankShootingSystem:
    def __init__(self, map: Map, eventManager: EventManager):
        self.__map = map
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__eventManager.addHandler(TankMovedEvent, self.onTankMoved)
        self.__tanks = {}
        self.__tankMap = {}
        self.__canShootTrough = ["Empty", "Base"]
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))

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
                "owner": ownerComponent
            }
            self.__tankMap[positionComponent.position] = tankId

    def onTankMoved(self, tankId: str, newPosition: positionTuple) -> None:
        if tankId in self.__tanks:
            self.__tankMap.pop(self.__tanks[tankId]["position"])
            self.__tanks[tankId]["position"] = newPosition
            self.__tankMap[newPosition] = tankId

    def getShootingOptions(self, tankId: str):
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
        
    def __distance(self, position1: positionTuple, position2: positionTuple) -> int:
        return (abs(position1[0] - position2[0]) + abs(position1[1] - position2[1]) + abs(position1[2] - position2[2])) // 2
    
    def __getCurvedShootingOptions(self, shooterTankId: str):
        shootingOptions = []

        shooterOwnerId = self.__tanks[shooterTankId]["owner"].ownerId
        shooterPosition = self.__tanks[shooterTankId]["position"]
        shootingComponent = self.__tanks[shooterTankId]["shooting"]

        for tankId, tankComponents in self.__tanks.items():
            if shooterOwnerId == tankComponents["owner"].ownerId:
                continue
            targetPosition = tankComponents["position"]
            distance = self.__distance(shooterPosition, targetPosition)

            if shootingComponent.minAttackRange <= distance <= shootingComponent.maxAttackRange:
                shootingOptions.append((targetPosition, [tankId]))

        return shootingOptions
    
    def __getDirectShootingTargets(self, ownerId, startingPosition, targetPermutation, maxAttackDistance):
        targets = []
        
        for distance in range(1, maxAttackDistance + 1):
            currentPosition = tuple(x + y * distance for x, y in zip(startingPosition, targetPermutation))
            if self.__map.objectAt(currentPosition) in self.__canShootTrough:
                targetTankId = self.__tankMap.get(currentPosition)

                if targetTankId:
                    if ownerId != self.__tanks[targetTankId]["owner"].ownerId:
                        targets.append(targetTankId)

        return targets

    def __getDirectShootingOptions(self, shooterTankId: str):
        shootingOptions = []

        shooterOwnerId = self.__tanks[shooterTankId]["owner"].ownerId
        shooterPosition = self.__tanks[shooterTankId]["position"]
        shootingComponent = self.__tanks[shooterTankId]["shooting"]
        

        for permutation in self.__hexPermutations:
            shootingDirection = tuple(x + y for x, y in zip(shooterPosition, permutation))
            shootingOptions.append((shootingDirection, self.__getDirectShootingTargets(shooterOwnerId, shooterPosition, permutation, shootingComponent.maxAttackDistance)))

        return [shootingOption for shootingOption in shootingOptions if len(shootingOption[1])]
    
    def shoot(self, shooterId: str, targetPosition: positionTuple):

        shooter = self.__tanks.get(shooterId)
        if shooter:
            shootingComponent = shooter["shooting"]
            shooterPosition = shooter["position"]
            shooterOwnerId = shooter["owner"].ownerId

            if isinstance(shootingComponent, CurvedShootingComponent):
                targets = []
                if not targetPosition in self.__tankMap:
                    pass
                if shootingComponent.minAttackRange > self.__distance(targetPosition , shooterPosition) > shootingComponent.maxAttackRange:
                    pass

                targetId = self.__tankMap[targetPosition]
                target = self.__tanks[targetId]
                if shooterOwnerId != target["owner"].ownerId:
                    targets.append(targetId)
            elif isinstance(shootingComponent, DirectShootingComponent):
                targets = []
                permutation = tuple(x - y for x, y in zip(targetPosition, shooterPosition))

                if not permutation in self.__hexPermutations:
                    pass

                targets = self.__getDirectShootingTargets(shooterOwnerId, shooterPosition, permutation, shootingComponent.maxAttackDistance)
            else:
                raise KeyError(f"Unknown shooting component {type(shootingComponent).__name__} for TankId:{shooterId}")
            
            for targetId in targets:
                self.__eventManager.triggerEvent(TankShotEvent, targetId, shootingComponent.damage)

