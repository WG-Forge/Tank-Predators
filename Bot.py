from Map import Map
from Aliases import positionTuple
import math
import random
from Events.Events import TankAddedEvent
from Tanks.Tank import Tank
from Events.EventManager import EventManager
from Tanks.AT_SPG import AT_SPG
from Tanks.HEAVY_TANK import HEAVY_TANK
from Tanks.LIGHT_TANK import LIGHT_TANK
from Tanks.MEDIUM_TANK import MEDIUM_TANK
from Tanks.SPG import SPG
from copy import deepcopy
from collections import deque
from Constants import HexTypes
import itertools
import heapq


class Bot:
    settings = {
        "CaptureBaseValue": 1,
        "CaptureDistanceMultiplier": 0.95,
        "HealthPercentLossMultiplier": 0.1,
        # new postion
        "RepairPositionBonus": 0.3,
        "CatapultPositionBonus": 0.3,
    }

    def __init__(self, map: Map, eventManager: EventManager, movementSystem, shootingSystem,
                 entityManagementSystem):
        """
        Initializes the bot.

        :param map: An instance of the Map that holds static game information.
        """
        self.__map = map
        self.__canMoveTo = {HexTypes.EMPTY.value, HexTypes.BASE.value, HexTypes.CATAPULT.value,
                            HexTypes.LIGHT_REPAIR.value, HexTypes.HARD_REPAIR.value}
        self.__mapSize = self.__map.getSize()
        self.__baseMap = {}
        self.__catapultMap = {}
        self.__hexPermutations = list(itertools.permutations([-1, 0, 1], 3))
        self.__teams = {}
        self.__initializeMap()
        self.__movementSystem = movementSystem
        self.__shootingSystem = shootingSystem
        self.__tanks = {}
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__entityManagementSystem = entityManagementSystem
        self.__turnOrder = [SPG, LIGHT_TANK, HEAVY_TANK, MEDIUM_TANK, AT_SPG]
        self.__player = entityManagementSystem.getOurPlayer()

    def getTanks(self) -> dict[Tank]:
        return self.__tanks

    def __initializeMap(self):
        """
        Initializes each positions value based on distance from a base
        """

        for position, obj in self.__map:
            if obj == HexTypes.BASE.value:
                self.__path(position, self.__baseMap, Bot.settings["CaptureBaseValue"],
                            Bot.settings["CaptureDistanceMultiplier"])

    def __distance(self, position1: positionTuple, position2: positionTuple) -> int:
        """
        Returns the distance between two positions.

        :param position1: The first position.
        :param position2: The second position.
        :return: The distance between the two positions.
        """
        return (abs(position1[0] - position2[0]) + abs(position1[1] - position2[1]) + abs(
            position1[2] - position2[2])) // 2

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the bot

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        self.__tanks[tankId] = tankEntity
        ownerId = tankEntity.getComponent("owner").ownerId
        self.__teams.setdefault(ownerId, []).append(tankId)

    def __path(self, position: positionTuple, valueMap, baseValue, distanceMultiplier):
        visited = set()  # Set to store visited offsets
        valueMap[position] = max(baseValue, valueMap.get(position, -math.inf))
        queue = deque()
        queue.append((position, 0))
        visited.add(position)

        # Perform breadth-first search to find all possible moves
        while len(queue) > 0:
            currentPosition, currentDistance = queue.popleft()
            currentPositionObject = self.__map.objectAt(currentPosition)
            if not (currentPositionObject in self.__canMoveTo):
                continue

            currentValue = valueMap.get(currentPosition)
            value = baseValue * (distanceMultiplier ** currentDistance)
            if currentValue:
                valueMap[currentPosition] = max(value, currentValue * value)
            else:
                valueMap[currentPosition] = value

            for permutation in self.__hexPermutations:
                newPosition = tuple(x + y for x, y in zip(currentPosition, permutation))
                if all(abs(pos) < self.__mapSize for pos in newPosition) and newPosition not in visited:
                    visited.add(newPosition)
                    queue.append((newPosition, currentDistance + 1))

    def __getEnemyTanks(self, allyOwnerId: int, damagedEnemies):
        enemyTanks = []
        for ownerId, tanks in self.__teams.items():
            if ownerId != allyOwnerId:
                enemyList = []
                for tankId in tanks:
                    if tankId in damagedEnemies:
                        if damagedEnemies[tankId] > 0:
                            enemyList.append(tankId)
                    else:
                        enemyList.append(tankId)
                if len(damagedEnemies) == 0:
                    enemyTanks.append(enemyList)
                elif len(enemyTanks) > 0:
                    enemyTanks[0].extend(enemyList)
                else:
                    enemyTanks.append(enemyList)
                
        return enemyTanks

    def __getPositions(self, tanks: list[int]):
        positions = []

        for tankId in tanks:
            positions.append(self.__tanks[tankId].getComponent("position").position)

        return positions

    def __getTotalDamages(self, tanks: list[int]):
        totalDamages = {}

        for tankId in tanks:
            targetablePositions = self.__shootingSystem.getShootablePositions(tankId)
            damage = self.__tanks[tankId].getComponent("shooting").damage

            for position in targetablePositions:
                totalDamages[position] = totalDamages.get(position, 0) + damage

        return totalDamages

    def __getMinBase(self, currentPosition):
        minDistance = math.inf
        for position, obj in self.__map:
            if obj == HexTypes.BASE.value:
                minDistance = min(minDistance, self.__distance(position, currentPosition))

        if minDistance > 0:
            return 1 / minDistance
        else:
            return 2
                
    def __buildHeuristicMap(self, tank, tankId, movementOptions, currentPosition, damagedEnemies):
        tank = self.__tanks[tankId]
        valueMap = {position: self.__getMinBase(position) for position in movementOptions}
        valueMap[currentPosition] = self.__getMinBase(currentPosition)
        ownerId = tank.getComponent("owner").ownerId
        healthComponent = tank.getComponent("health")
        selfDestructionReward = tank.getComponent("destructionReward").destructionReward
        hasCatapult = tank.getComponent("shooting").rangeBonusEnabled
        maxHP = healthComponent.maxHealth
        currentHP = healthComponent.currentHealth

        enemyTanks = self.__getEnemyTanks(ownerId, damagedEnemies)

        # adjust values based on potential enemy targets that are capturing
        for position in valueMap.keys():
            totalValue = 0
            obj = self.__map.objectAt(position)
            if obj == HexTypes.LIGHT_REPAIR.value:
                if isinstance(tank, MEDIUM_TANK):
                    totalValue += (Bot.settings["RepairPositionBonus"] * (maxHP - currentHP))
            elif obj == HexTypes.HARD_REPAIR.value:
                if isinstance(tank, (AT_SPG, HEAVY_TANK)):
                    totalValue += (Bot.settings["RepairPositionBonus"] * (maxHP - currentHP))
            elif obj == HexTypes.CATAPULT.value and self.__shootingSystem.catapultAvailable(position) and not hasCatapult:
                totalValue += Bot.settings["CatapultPositionBonus"]

            valueMap[position] += totalValue

        # adjust values based on potential damage taken
        damageValues = []
        for enemyTankList in enemyTanks:
            currentIndex = len(damageValues)
            damageValues.append({})

            totalDamages = self.__getTotalDamages(enemyTankList)
            for position, totalDamage in totalDamages.items():
                if position in valueMap:
                    healthPartLeft = ((currentHP - totalDamage) / currentHP)
                    if healthPartLeft <= 0:
                        obj = self.__map.objectAt(position)
                        if (obj == "LightRepair" and isinstance(tank, MEDIUM_TANK)) or (obj == "HardRepair" and isinstance(tank, (AT_SPG, HEAVY_TANK))):
                            continue
                        damageValues[currentIndex][position] = -selfDestructionReward
                    else:
                        healthValueLost = (1 - healthPartLeft) * Bot.settings["HealthPercentLossMultiplier"]
                        damageValues[currentIndex][position] = (1 - healthValueLost)

        if len(damageValues) > 1:
            for position, value in damageValues[1].items():
                    if value < damageValues[0].get(position, math.inf):
                        damageValues[0][position] = value

        if len(damageValues) > 0:
            for key, value in damageValues[0].items():
                valueMap[key] *= value

        return valueMap     

    def __getBestMove(self, moves: list[positionTuple], tankId: int, damagedEnemies) -> list[positionTuple]:
        tank = self.__tanks[tankId]
        currentPosition = tank.getComponent("position").position
        heuristicMap = self.__buildHeuristicMap(tank, tankId, moves, currentPosition, damagedEnemies)
        heuristicMap.pop(currentPosition)
        return [k for k, v in heapq.nlargest(1, heuristicMap.items(), key=lambda item: item[1])]

    def __getTileTypesInRange(self, movementOptions: list[positionTuple]) -> set:
        """
        Returns list of all tile types in movement range
        """
        tileTypes = set()
        for position in movementOptions:
            tileTypes.add(self.__map.objectAt(position))

        return tileTypes

    @staticmethod
    def __isHealingPossible(allyTank: Tank, allTileTypes: set[str]) -> bool:
        """
        :param: allyTank Tank object
        :param: allTileTypes tile types that are reachable
        :return: true if healing is possible in one move, false otherwise
        """
        return (type(allyTank).__name__ == "MEDIUM_TANK" and HexTypes.LIGHT_REPAIR.value in allTileTypes) \
               or (type(allyTank).__name__ in ("HEAVY_TANK", "AT_SPG") and HexTypes.HARD_REPAIR.value in allTileTypes)

    # TODO: Improve evaluation
    def __evaluateCurrentActions(self, currentActions, movement, damagedEnemies):
        positionValue = 0
        for tankId, positionChange in movement.items():
            positionValue += self.__buildHeuristicMap(self.__tanks[tankId], tankId, [], positionChange[1], damagedEnemies)[positionChange[1]]

        capturePointsDenied = 0
        destructionPoints = 0
        totalDamage = 0
        for damagedEnemyId, health in damagedEnemies.items():
            targetHealth = self.__tanks[damagedEnemyId].getComponent("health").currentHealth
            totalDamage += targetHealth - health
            if health <= 0:
                capturePointsDenied += self.__tanks[damagedEnemyId].getComponent("capture").capturePoints
                destructionPoints += self.__tanks[damagedEnemyId].getComponent("destructionReward").destructionReward

        return positionValue + 3 ** (capturePointsDenied - 1) + destructionPoints * 1.3 + totalDamage * 0.05
    
    def __findBestActionCombination(self):
        bestScore = -math.inf
        bestActions = []
        totalCombos = 0

        def backtrack(currentActions, currentTankIndex, movement, damagedEnemies):
            nonlocal bestScore, bestActions, totalCombos

            if currentTankIndex == 5:
                totalCombos += 1
                # Evaluate the current move combination and update the best score and moves
                score = self.__evaluateCurrentActions(currentActions, movement, damagedEnemies)
                if score > bestScore:
                    bestScore = score
                    bestActions = deepcopy(currentActions)
                return

            currentTankId = self.__player.getPlayerTanks()[currentTankIndex]
            possibleMovement = self.__movementSystem.getMovementOptions(currentTankId)
            possibleShoting = self.__shootingSystem.getShootingOptions(currentTankId)
            currentPosition = self.__tanks[currentTankId].getComponent("position").position
            
            targetPositions = self.__getBestMove(possibleMovement, currentTankId, damagedEnemies)
            for targetPosition in targetPositions:
                currentActions.append(("move", currentTankId, targetPosition))
                self.__movementSystem.move(currentTankId, targetPosition)
                movement[currentTankId] = [currentPosition, targetPosition]
                backtrack(currentActions, currentTankIndex + 1, movement, damagedEnemies)
                self.__movementSystem.move(currentTankId, currentPosition)
                del movement[currentTankId]
                currentActions.pop()

            currentDamage = self.__tanks[currentTankId].getComponent("shooting").damage
            for targetPosition, targets in possibleShoting:
                shot = False
                damagedEnemiesBacktrack = deepcopy(damagedEnemies)
                for target in targets:
                    if target in damagedEnemiesBacktrack:
                        targetHealth = damagedEnemiesBacktrack[target]
                    else:
                        targetHealth = self.__tanks[target].getComponent("health").currentHealth

                    if targetHealth > 0:
                        shot = True
                        damagedEnemiesBacktrack[target] = targetHealth - currentDamage

                if shot:
                    currentActions.append(("shoot", currentTankId, targetPosition))
                    backtrack(currentActions, currentTankIndex + 1, movement, damagedEnemiesBacktrack)
                    currentActions.pop()

            backtrack(currentActions, currentTankIndex + 1, movement, damagedEnemies)

        backtrack([], 0, {}, {})

        return bestActions

    def getActions(self) -> tuple[str, positionTuple]:
        return self.__findBestActionCombination()

        # either shooting chosen and no shooting options, or move chosen and no move options
        return "none", (-1, -1, -1)

    def reset(self) -> None:
        """
        Resets the bot it's initial state.
        """
        self.__tanks.clear()
        self.__teams.clear()
