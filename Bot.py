from Map import Map
from Aliases import positionTuple, shootingOptionsList
import math
import random
from Events.Events import TankAddedEvent
from Tanks.Tank import Tank
from Events.EventManager import EventManager
from copy import deepcopy

class Bot:
    settings = {
        "CaptureBaseValue": 1,
        "CaptureDistanceMultiplier": 0.95,
        "HealthPercentLossMultiplier": 0.1
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
                self.__path(position, self.__baseMap, self.__mapSize * 2, Bot.settings["CaptureBaseValue"], Bot.settings["CaptureDistanceMultiplier"])

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the bot

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        self.__tanks[tankId] = tankEntity
        ownerId = tankEntity.getComponent("owner").ownerId
        self.__teams.setdefault(ownerId, []).append(tankId)

    def __path(self, position: positionTuple, valueMap, distance, baseValue, distanceMultiplier):
        visited = set()  # Set to store visited offsets
        visited.add((0, 0, 0))  # Can always reach 0 offset since we are already there
        valueMap[position] = max(baseValue, valueMap.get(position, -math.inf))

        # Perform breadth-first search to find all possible moves
        for currentDistance in range(1, distance + 1):
            for offsetPosition, canBeReachedBy in self.__pathingOffsets[currentDistance].items():
                if not len(visited.intersection(canBeReachedBy)) > 0:
                    continue # can't be reached

                currentPosition = tuple(x + y for x, y in zip(position, offsetPosition))
                if not all(abs(pos) < self.__mapSize for pos in currentPosition):
                    continue # outside of map borders

                currentPositionObject = self.__map.objectAt(currentPosition)
                if not (currentPositionObject in self.__canMoveTo):
                    continue # tanks can't move there

                visited.add(offsetPosition)
                currentValue = valueMap.get(currentPosition)
                value = baseValue * (distanceMultiplier ** currentDistance)
                if currentValue:
                    valueMap[currentPosition] = max(value, currentValue * value)
                else:
                    valueMap[currentPosition] = value

    def __getEnemyTanks(self, allyOwnerId: int):
        enemyTanks = []
        for ownerId, tanks in self.__teams.items():
            if ownerId != allyOwnerId:
                enemyTanks.extend(tanks)
        
        return enemyTanks
    
    def __getTotalDamages(self, tanks: list[int]):
        totalDamages = {}

        for tankId in tanks:
            targetablePositions = self.__shootingSystem.getShootablePositions(tankId)
            damage = self.__tanks[tankId].getComponent("shooting").damage

            for position in targetablePositions:
                totalDamages[position] = totalDamages.get(position, 0) + damage
        
        return totalDamages

    def __buildHeuristicMap(self, tank: Tank):
        valueMap = deepcopy(self.__baseMap)
        ownerId = tank.getComponent("owner").ownerId
        healthComponent = tank.getComponent("health")
        maxHP = healthComponent.maxHealth
        currentHP = healthComponent.currentHealth

        enemyTanks = self.__getEnemyTanks(ownerId)

        totalDamages = self.__getTotalDamages(enemyTanks)

        for position, totalDamage in totalDamages.items():
            if position in valueMap:
                healthValueLost = (1 - ((currentHP - totalDamage) / currentHP)) * Bot.settings["HealthPercentLossMultiplier"]
                valueMap[position] *= (1 - healthValueLost)

        return valueMap      

    def __getBestMove(self, moves: list, tank: Tank) -> list[positionTuple]:
        heuristicMap = self.__buildHeuristicMap(tank)
        currentPosition = tank.getComponent("position").position
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
            bestOption = self.__getBestMove(movementOptions, tank)
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
