from Map import Map
from Events.EventManager import EventManager
import Tanks.Settings as TankSettings
from TankManagement.TankManager import TankManager
from TankSystems.TankMovementSystem import TankMovementSystem
from TankSystems.TankShootingSystem import TankShootingSystem
from TankSystems.TankHealthSystem import TankHealthSystem
from TankSystems.DisplaySystem import DisplaySystem
from TankSystems.TankRespawnSystem import TankRespawnSystem
from TankSystems.PositionBonusSystem import PositionBonusSystem
import inspect
import Events.Events as AllEvents
from Aliases import jsonDict, positionTuple
from Utils import PathingOffsets
from Bot import Bot

class World():
    def __init__(self, map: jsonDict, gameState: jsonDict) -> None:
        self.__map = Map(map)
        self.__pathingOffsets = PathingOffsets(self.__map.getSize())
        self.__initializeEventManager()
        self.__tankManager = TankManager(self.__eventManager)
        self.__initializeSystems(gameState)
        self.__bot = Bot(self.__map, self.__pathingOffsets, self.__movementSystem, self.__shootingSystem)

    def __initializeEventManager(self):
        self.__eventManager = EventManager()
        allEvents = inspect.getmembers(AllEvents, inspect.isclass)
        # init all events
        for _, cls in allEvents:
            self.__eventManager.registerEvent(cls)

    def __initializeSystems(self, gameState: jsonDict):
        self.__movementSystem = TankMovementSystem(self.__map, self.__eventManager, self.__pathingOffsets)
        self.__displaySystem = DisplaySystem(self.__map, self.__eventManager)
        self.__shootingSystem = TankShootingSystem(self.__map, self.__eventManager, self.__pathingOffsets, gameState["attack_matrix"], gameState["catapult_usage"])
        self.__healthSystem = TankHealthSystem(self.__eventManager)
        self.__respawnSystem = TankRespawnSystem(self.__eventManager)
        self.__positionBonusSystem = PositionBonusSystem(self.__map, self.__eventManager)

    def resetSystems(self, gameState: jsonDict):
        self.__tankManager.reset()
        self.__displaySystem.reset()
        self.__movementSystem.reset()
        self.__shootingSystem.reset(gameState["attack_matrix"], gameState["catapult_usage"])
        self.__healthSystem.reset()
        self.__respawnSystem.reset()
        self.__positionBonusSystem.reset()
        self.__bot.reset()

    def addMissingTanks(self, gameState: jsonDict):
        for tankId, tankData in gameState["vehicles"].items():
            tankId = str(tankId)
            if not self.__tankManager.hasTank(tankId):
                self.__tankManager.addTank(tankId, tankData)

    def shoot(self, tankId: str, targetPosition: positionTuple):
        self.__shootingSystem.shoot(tankId, targetPosition)

    def move(self, tankId: str, targetPosition: positionTuple):
        self.__movementSystem.move(tankId, targetPosition)

    def getBot(self):
        return self.__bot
    
    def turn(self, currentPlayer: int):
        self.__respawnSystem.turn()
        self.__positionBonusSystem.turn()
        self.__displaySystem.turn()
        self.__shootingSystem.turn(currentPlayer)

    def quit(self):
        self.__displaySystem.quit()
