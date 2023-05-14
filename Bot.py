from Map import Map
from Aliases import positionTuple, shootableTanksDict, shootingOptionsList
import math
import random
from Constants import GameConstants
from Events.Events import TankAddedEvent
from Tanks.Tank import Tank
from Events.EventManager import EventManager


class Bot:
    settings = {
        "CaptureDistanceMultiplier": 0.95
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
        self.__initializeMap()
        self.__movementSystem = movementSystem
        self.__shootingSystem = shootingSystem
        self.__tanks = {}
        self.__eventManager = eventManager
        self.__eventManager.addHandler(TankAddedEvent, self.onTankAdded)
        self.__entityManagementSystem = entityManagementSystem

    def __initializeMap(self):
        """
        Initializes each positions value based on distance from a base
        """

        self.__valueMap = {}

        for position, obj in self.__map:
            if obj == "Base":
                self.__pathFromBase(position)

    def onTankAdded(self, tankId: str, tankEntity: Tank) -> None:
        """
        Event handler. Adds the tank to the system if it has shooting, owner and position components

        :param tankId: The ID of the added tank.
        :param tankEntity: The Tank entity that was added.
        """
        self.__tanks[tankId] = tankEntity

    def __pathFromBase(self, basePosition: positionTuple):
        # Gets the tanks maximum movement distance
        distance = self.__map.getSize()
        mapSize = distance
        distanceMultiplier = Bot.settings["CaptureDistanceMultiplier"]
        visited = set()  # Set to store visited offsets
        visited.add((0, 0, 0))  # Can always reach 0 offset since we are already there
        self.__valueMap[basePosition] = 1

        # Perform breadth-first search to find all possible moves
        for currentDistance in range(1, distance + 1):
            # Iterate over all possible offsets for the current distance
            for offsetPosition, canBeReachedBy in self.__pathingOffsets[currentDistance].items():
                # Check if the offset can be reached from a previously reachable position
                if len(visited.intersection(canBeReachedBy)) > 0:
                    currentPosition = tuple(x + y for x, y in zip(basePosition, offsetPosition))
                    # Check if the current position is within the boundaries of the game map
                    if abs(currentPosition[0]) < mapSize and abs(currentPosition[1]) < mapSize and abs(
                            currentPosition[2]) < mapSize:
                        currentPositionObject = self.__map.objectAt(currentPosition)
                        # Check if the tank can move through the current position
                        if currentPositionObject in self.__canMoveTo and currentPositionObject != "Base":
                            currentValue = self.__valueMap.get(currentPosition, -math.inf)
                            newValue = distanceMultiplier ** (currentDistance - 1)
                            if newValue >= currentValue:
                                visited.add(offsetPosition)
                                self.__valueMap[currentPosition] = newValue
        print(self.__valueMap)

    def __getBestMove(self, moves: list) -> list[positionTuple]:
        maxValue = -math.inf
        maxPositions = []

        for move in moves:
            value = self.__valueMap[move]
            if value > maxValue:
                maxPositions.clear()
                maxPositions.append(move)
                maxValue = value
            elif value == maxValue:
                maxPositions.append(move)

        return maxPositions

    def __getTileTypesInRange(self, movementOptions: list[positionTuple]) -> set:
        """
        Returns list of all tile types in movement range
        """
        tileTypes = set()
        for position in movementOptions:
            tileTypes.add(self.__map.objectAt(position))

        return tileTypes

    def __healingModifier(self, allyTank, allTileTypes, totalTargetsDamage) -> float:
        allyHealth = allyTank.getComponent("health").currentHealth
        healingPossible = self.__isHealingPossible(allyTank, allTileTypes)
        if allyHealth <= totalTargetsDamage:
            if healingPossible:
                return ActionModifier.HEALING_IN_RANGE_DESTROY_THREAT.value
            else:
                return ActionModifier.DESTROY_THREAT.value
        else:
            if healingPossible:
                return ActionModifier.HEALING_IN_RANGE_NO_THREAT.value

    @staticmethod
    def __isHealingPossible(allyTank: Tank, allTileTypes: set[str]) -> bool:
        """
        :param: allyTank Tank object
        :param: allTileTypes tile types that are reachable
        :return: true if healing is possible in one move, false otherwise
        """
        return (type(allyTank).__name__ == "MEDIUM_TANK" and "LightRepair" in allTileTypes) \
               or (type(allyTank).__name__ in ("HEAVY_TANK", "AT_SPG") and "HeavyRepair" in allTileTypes)

    def __getBestTarget(self, tankId: str, shootingOptions: shootingOptionsList):
        shootingOptionsInfo = dict()
        allyTank = self.__tanks[tankId]
        allyTankDamage = allyTank.getComponent("shooting").damage

        for shootingPosition, enemyTankIds in shootingOptions:
            destroyableTanks = 0
            capturePoints = 0
            for enemyTankId in enemyTankIds:
                enemyTank = self.__tanks[enemyTankId]
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

    def getAction(self, tankId: str) -> tuple[str, positionTuple]:
        movementOptions = self.__movementSystem.getMovementOptions(tankId)
        shootingOptions = self.__shootingSystem.getShootingOptions(tankId)
        if len(shootingOptions) > 0:
            bestShootingOption = self.__getBestTarget(tankId, shootingOptions)
            return "shoot", bestShootingOption
        if len(movementOptions) > 0:
            bestOptions = self.__getBestMove(movementOptions)
            randomChoice = random.randint(0, len(bestOptions) - 1)
            return "move", bestOptions[randomChoice]

        # either shooting chosen and no shooting options, or move chosen and no move options
        return "none", (-1, -1, -1)

    def reset(self) -> None:
        """
        Resets the bot it's initial state.
        """
        self.__tanks.clear()
