from Map import Map
from Aliases import positionTuple, shootingOptionsList
import math
import random
from Constants import ShootingModifier

class Bot:
    settings = {
        "CaptureDistanceMultiplier": 0.95
    }

    def __init__(self, map: Map, pathingOffsets, movementSystem, shootingSystem):
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

    def __initializeMap(self):
        """
        Initializes each positions value based on distance from a base
        """

        self.__valueMap = {}

        for position, obj in self.__map:
            if obj == "Base":
                self.__pathFromBase(position)

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
                            newValue = distanceMultiplier**(currentDistance - 1)
                            if newValue >= currentValue:
                                visited.add(offsetPosition)
                                self.__valueMap[currentPosition] = newValue

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
    
    def __getBestTarget(self, tankID: str, shootingOptions: shootingOptionsList) -> tuple[positionTuple, int]:
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
      
    def getAction(self, tankId: str):
        options = self.__shootingSystem.getShootingOptions(tankId)
        if len(options) > 0:
            maxTuple, maxModifier = self.__getBestTarget(tankId, options)
            if maxModifier != -1:
                return ("shoot", maxTuple)

        options = self.__movementSystem.getMovementOptions(tankId)
        if len(options) > 0:
            bestOptions = self.__getBestMove(options)
            randomChoice = random.randint(0, len(bestOptions) - 1)
            return ("move", bestOptions[randomChoice])


            

                   
