from Map import Map
from Events.EventManager import EventManager
from TankManagement.TankManager import TankManager
from TankSystems.TankMovementSystem import TankMovementSystem
from TankSystems.TankShootingSystem import TankShootingSystem
from TankSystems.TankHealthSystem import TankHealthSystem
from TankSystems.DisplaySystem import DisplaySystem
from TankSystems.TankRespawnSystem import TankRespawnSystem
from TankSystems.PositionBonusSystem import PositionBonusSystem
from TankSystems.BaseCaptureSystem import BaseCaptureSystem
import inspect
import Events.Events as AllEvents
from Aliases import jsonDict, positionTuple
from Utils import PathingOffsets
from Bot import Bot
from Entities.EntityManagementSystem import EntityManagementSystem

class World():
    def __init__(self, map: jsonDict, gameState: jsonDict) -> None:
        """
        Initializes the game world.

        :param map: A dictionary containing the map data.
        :param gameState: A dictionary containing the game state data.
        """
        self.__map = Map(map)
        self.__pathingOffsets = PathingOffsets(self.__map.getSize())
        self.__initializeEventManager()
        self.__tankManager = TankManager(self.__eventManager)
        self.__initializeSystems(gameState)
        self.__bot = Bot(self.__map, self.__pathingOffsets, self.__eventManager, self.__movementSystem, self.__shootingSystem)

    def __initializeEventManager(self) -> None:
        """
        Initializes the event manager.
        """
        self.__eventManager = EventManager()

        # init all events
        allEvents = inspect.getmembers(AllEvents, inspect.isclass)
        for _, cls in allEvents:
            self.__eventManager.registerEvent(cls)

    def __initializeSystems(self, gameState: jsonDict) -> None:
        """
        Initializes the various systems used in the game world.

        :param gameState: A dictionary containing the game state data.
        """
        self.__movementSystem = TankMovementSystem(self.__map, self.__eventManager, self.__pathingOffsets)
        self.__displaySystem = DisplaySystem(self.__map, self.__eventManager)
        self.__shootingSystem = TankShootingSystem(self.__map, self.__eventManager, self.__pathingOffsets, gameState["attack_matrix"], gameState["catapult_usage"])
        self.__healthSystem = TankHealthSystem(self.__eventManager)
        self.__respawnSystem = TankRespawnSystem(self.__eventManager)
        self.__positionBonusSystem = PositionBonusSystem(self.__map, self.__eventManager)
        self.__baseCaptureSystem = BaseCaptureSystem(self.__map, self.__eventManager)
        self.__entityManagementSystem = EntityManagementSystem(gameState)

    def resetSystems(self, gameState: jsonDict) -> None:
        """
        Resets the various systems used in the game world to their initial state.

        :param gameState: A dictionary containing the game state data.
        """
        self.__tankManager.reset()
        self.__displaySystem.reset()
        self.__movementSystem.reset()
        self.__shootingSystem.reset(gameState["attack_matrix"], gameState["catapult_usage"])
        self.__healthSystem.reset()
        self.__respawnSystem.reset()
        self.__positionBonusSystem.reset()
        self.__baseCaptureSystem.reset()
        self.__bot.reset()
        self.__entityManagementSystem.reset()

    def getEntityManagementSystem(self):
        return self.__entityManagementSystem

    def addMissingTanks(self, gameState: jsonDict) -> None:
        """
        Adds tanks that are in the game state but not in the local world.

        :param gameState: A dictionary containing the game state data.
        """
        for tankId, tankData in gameState["vehicles"].items():
            tankId = str(tankId)
            if not self.__tankManager.hasTank(tankId):
                self.__tankManager.addTank(tankId, tankData)

    def shoot(self, tankId: str, targetPosition: positionTuple) -> None:
        """
        Shoots at a target position.

        :param tankId: The ID of the tank doing the shooting.
        :param targetPosition: The position being targeted.
        """
        self.__shootingSystem.shoot(tankId, targetPosition)

    def move(self, tankId: str, targetPosition: positionTuple) -> None:
        """
        Moves a tank to a target position.

        :param tankId: The ID of the tank being moved.
        :param targetPosition: The position being moved to.
        """
        self.__movementSystem.move(tankId, targetPosition)

    def getBot(self) -> Bot:
        """
        Gets the game's bot.

        :return: The game's bot.
        """
        return self.__bot
    
    def turn(self, currentPlayer: int) -> None:
        """
        Performs the turn logic for the game world.
        
        :param currentPlayer: ID of the player whose turn it is.
        """
        self.__respawnSystem.turn()
        self.__positionBonusSystem.turn()
        self.__baseCaptureSystem.turn()
        self.__displaySystem.turn()
        self.__shootingSystem.turn(currentPlayer)

    def round(self) -> None:
        """
        Performs the round logic for the game world.
        
        :param currentPlayer: ID of the player whose turn it is.
        """
        self.__baseCaptureSystem.round()

    def quit(self):
        """
        Quits the game by closing the display.
        """
        self.__displaySystem.quit()
