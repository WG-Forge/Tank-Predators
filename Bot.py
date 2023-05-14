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
        "CatapultBaseValue": 1,
        "CatapultDistanceMultiplier": 0.95,
        "HealthPercentLossMultiplier": 0.1,
        "PositionTargetsInCaptureMultiplier": 1.01,
    }

    def __init__(self, map: Map, pathingOffsets, eventManager: EventManager, movementSystem, shootingSystem,
                 entityManagementSystem):
        """
        Initializes the bot.

        :param map: An instance of the Map that holds static game information.
        :param pathingOffsets: A list of dictionaries representing all possible positions a target can move to in a given number of steps 
        """
        self.__map = map
        self.__pathingOffsets = pathingOffsets
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
    
    def __initializeCatapults(self, tankPosition):
        """
        Initializes each positions value based on distance from a catapult
        """
        closest = None
        closestDistance = math.inf
        for position, obj in self.__map:
            if obj == "Catapult" and self.__shootingSystem.catapultAvailable(position):
                distance = self.__distance(tankPosition, position)
                if distance < closestDistance:
                    closest = position
                    closestDistance = distance
        if closest:
            self.__path(closest, self.__catapultMap, Bot.settings["CatapultBaseValue"], Bot.settings["CatapultDistanceMultiplier"])
            return True
        return False
            

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
        queue.append(((position), 0))
        visited.add(position)

        # Perform breadth-first search to find all possible moves
        while len(queue) > 0:
            currentPosition, currentDistance = queue.popleft()
            print(currentPosition)
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

    def __buildHeuristicMap(self, tank: Tank, tankId: int, moves: list[positionTuple], currentPosition: positionTuple):
        mapToUse = self.__baseMap
        
        if True:#isinstance(tank, (LIGHT_TANK, MEDIUM_TANK)):
            hasCatapult = tank.getComponent("shooting").rangeBonusEnabled
            if not hasCatapult:
                success = self.__initializeCatapults(currentPosition)
                if success:
                    mapToUse = self.__catapultMap

        valueMap = {position: mapToUse[position] for position in moves}
        valueMap[currentPosition] = self.__baseMap[currentPosition]

        ownerId = tank.getComponent("owner").ownerId
        healthComponent = tank.getComponent("health")
        maxHP = healthComponent.maxHealth
        currentHP = healthComponent.currentHealth

        enemyTanks = self.__getEnemyTanks(ownerId)

        totalDamages = self.__getTotalDamages(enemyTanks)

        # adjust values based on potential damage taken
        for position, totalDamage in totalDamages.items():
            if position in valueMap:
                healthValueLost = (1 - ((currentHP - totalDamage) / currentHP)) * Bot.settings["HealthPercentLossMultiplier"]
                valueMap[position] *= (1 - healthValueLost)


        enemyPositions = self.__getPositions(enemyTanks)
        # adjust values based on potential enemy targets that are capturing
        for position in valueMap.keys():
            targetablePositions = self.__shootingSystem.getShootablePositions(tankId, position)
            enemyTargets = 0

            for targetPosition in targetablePositions:
                if targetPosition in enemyPositions and self.__map.objectAt(position) == "Base":
                    enemyTargets += 1
            valueMap[position] *= (Bot.settings["PositionTargetsInCaptureMultiplier"] ** enemyTargets)

        return valueMap     


    def __getBestMove(self, moves: list[positionTuple], tank: Tank, tankId: int) -> list[positionTuple]:
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
            return maxPositions[random.randint(0, totalOptions - 1)]
        else:
            return None

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

    def getAction(self, tankId: str) -> tuple[str, positionTuple]:
        movementOptions = self.__movementSystem.getMovementOptions(tankId)
        shootingOptions = self.__shootingSystem.getShootingOptions(tankId)
        tank = self.__tanks[tankId]
        if len(shootingOptions) > 0:
            bestShootingOption = tank.getBestTarget(shootingOptions, self.__tanks)
            return "shoot", bestShootingOption
        if len(movementOptions) > 0:
            bestOption = self.__getBestMove(movementOptions, tank, tankId)
            if bestOption:
                return "move", bestOption
            else:
                return None, None

        # either shooting chosen and no shooting options, or move chosen and no move options
        return "none", (-1, -1, -1)

    def reset(self) -> None:
        """
        Resets the bot it's initial state.
        """
        self.__tanks.clear()
