from Map import Map
from Aliases import positionTuple, shootingOptionsList
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
import itertools

class Bot:
    settings = {
        "CaptureBaseValue": 1,
        "CaptureDistanceMultiplier": 0.95,
        "HealthPercentLossMultiplier": 0.99,
        # new postion
        "RepairPositionBonus": 0.5,
        "CatapultPositionBonus": 0.5,
    }

    def __init__(self, map: Map, eventManager: EventManager, movementSystem, shootingSystem,
                 entityManagementSystem):
        """
        Initializes the bot.

        :param map: An instance of the Map that holds static game information.
        """
        self.__map = map
        self.__canMoveTo = {"Empty", "Base", "Catapult", "LightRepair", "HardRepair"}
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

    def getTanks(self) -> dict[Tank]:
        return self.__tanks

    def __initializeMap(self):
        """
        Initializes each positions value based on distance from a base
        """

        for position, obj in self.__map:
            if obj == "Base":
                self.__path(position, self.__baseMap, Bot.settings["CaptureBaseValue"], Bot.settings["CaptureDistanceMultiplier"])

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

    def currentUser(self, ownerId: int):
        self.__currentPlayerTanks = [None] * 5
        for tankId in self.__teams[ownerId]:
            self.__currentPlayerTanks[self.__turnOrder.index(type(self.__tanks[tankId]))] = tankId

    def __path(self, position: positionTuple, valueMap, baseValue, distanceMultiplier):
        visited = set()  # Set to store visited offsets
        valueMap[position] = max(baseValue, valueMap.get(position, -math.inf))
        queue = deque()
        queue.append(((position), 0))
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
                if all(abs(pos) < self.__mapSize for pos in newPosition) and not newPosition in visited:
                    visited.add(newPosition)
                    queue.append(((newPosition), currentDistance + 1))

    def __getEnemyTanks(self, allyOwnerId: int):
        enemyTanks = []
        for ownerId, tanks in self.__teams.items():
            if ownerId != allyOwnerId:
                enemyTanks.extend(tanks)
        
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
            if obj == "Base":
                minDistance = min(minDistance, self.__distance(position, currentPosition))

        if minDistance > 0:
            return 1 / minDistance
        else:
            return 2
                
    # TODO: Modify to take information from backtracking to remove dead enemies from enemyTanks (if any)
    def __buildHeuristicMap(self, tank, tankId, movementOptions, currentPosition):
        tank = self.__tanks[tankId]
        valueMap = {position: self.__baseMap[position] for position in movementOptions}
        valueMap[currentPosition] = self.__baseMap[currentPosition]
        ownerId = tank.getComponent("owner").ownerId
        healthComponent = tank.getComponent("health")
        hasCatapult = tank.getComponent("shooting").rangeBonusEnabled
        maxHP = healthComponent.maxHealth
        currentHP = healthComponent.currentHealth

        enemyTanks = self.__getEnemyTanks(ownerId)

        totalDamages = self.__getTotalDamages(enemyTanks)

        # adjust values based on potential enemy targets that are capturing
        for position in valueMap.keys():
            totalValue = 0
            obj = self.__map.objectAt(position)
            if obj == "LightRepair":
                if isinstance(tank, MEDIUM_TANK):
                    totalValue += (Bot.settings["RepairPositionBonus"] * (maxHP - currentHP))
            elif obj == "HardRepair":
                if isinstance(tank, (AT_SPG, HEAVY_TANK)):
                    totalValue += (Bot.settings["RepairPositionBonus"] * (maxHP - currentHP))
            elif obj == "Catapult" and self.__shootingSystem.catapultAvailable(position) and not hasCatapult:
                totalValue += Bot.settings["CatapultPositionBonus"]

            valueMap[position] += totalValue

        # # adjust values based on potential damage taken
        # for position, totalDamage in totalDamages.items():
        #     if position in valueMap:
        #         healthPartLeft = ((currentHP - totalDamage) / currentHP)
        #         if healthPartLeft <= 0:
        #             obj = self.__map.objectAt(position)
        #             if (obj == "LightRepair" and isinstance(tank, MEDIUM_TANK)) or (obj == "HardRepair" and isinstance(tank, (AT_SPG, HEAVY_TANK))):
        #                 continue
        #             valueMap[position] = 0
        #         else:
        #             healthValueLost = (1 - healthPartLeft) * Bot.settings["HealthPercentLossMultiplier"]
        #             valueMap[position] *= (1 - healthValueLost)

        return valueMap     

    # TODO: Modify getBestMove to provide multiple best moves since we have enough time for simulating
    def __getBestMove(self, moves: list[positionTuple], tankId: int) -> list[positionTuple]:
        tank = self.__tanks[tankId]
        currentPosition = tank.getComponent("position").position
        heuristicMap = self.__buildHeuristicMap(tank, tankId, moves, currentPosition)
        maxValue = heuristicMap[currentPosition]
        maxPositions = []

        for move in moves:
            value = heuristicMap[move]
            if value > maxValue:
                maxPositions.clear()
                maxPositions.append(move)
                maxValue = value
            elif value == maxValue:
                maxPositions.append(move)

        totalOptions = len(maxPositions) 
        if totalOptions > 0:
            chosenPosition = maxPositions[random.randint(0, totalOptions - 1)]
            return heuristicMap[currentPosition], chosenPosition, heuristicMap[chosenPosition]
        else:
            return heuristicMap[currentPosition], None, None

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
        return (type(allyTank).__name__ == "MEDIUM_TANK" and "LightRepair" in allTileTypes) \
               or (type(allyTank).__name__ in ("HEAVY_TANK", "AT_SPG") and "HeavyRepair" in allTileTypes)

    # TODO: Improve evaluation
    def __evaluateCurrentActions(self, currentActions, movement, damagedEnemies):
        score = 0
        for tankId, positionChange in movement.items():
            score += (-self.__distance(positionChange[1], (0, 0, 0)) + self.__distance(positionChange[0], (0, 0, 0)))

        for damagedEnemyId, health in damagedEnemies.items():
            if health <= 0:
                score += self.__tanks[damagedEnemyId].getComponent("capture").capturePoints
                score += self.__tanks[damagedEnemyId].getComponent("destructionReward").destructionReward

        return score
    
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

            currentTankId = self.__currentPlayerTanks[currentTankIndex]
            possibleMovement = self.__movementSystem.getMovementOptions(currentTankId)
            possibleShoting = self.__shootingSystem.getShootingOptions(currentTankId)
            currentPosition = self.__tanks[currentTankId].getComponent("position").position
            
            # TODO: Modify getBestMove to provide multiple best moves since we have enough time for simulating
            # for targetPosition in possibleMovement:
            currentValue, targetPosition, targetValue = self.__getBestMove(possibleMovement, currentTankId)
            if targetPosition:
            # if valueMap[targetPosition] > valueMap[currentPosition]:
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
