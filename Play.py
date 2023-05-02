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
import random
import inspect
import Events.Events as AllEvents
from Exceptions import BadCommandException, AccessDeniedException, InappropriateGameStateException, TimeoutException, \
    InternalServerErrorException
from PlayerSession import PlayerSession
from Utils import HexToTuple
from Utils import TupleToHex
from ServerConnection import Action
import logging
from Aliases import jsonDict
from Utils import PathingOffsets
from Bot import Bot


class Game:
    def __init__(self, session: PlayerSession, data: jsonDict) -> None:
        self.__session = session
        self.__playerID = self.__session.login(data)

        # Get static map data
        mapInfo = self.__session.getMapInfo()
        self.__map = Map(mapInfo)
        self.__pathingOffsets = PathingOffsets(self.__map.getSize())
        self.__bot = Bot(self.__map, self.__pathingOffsets)
        self.__initializeWorld()
        self.__play()
        self.__session.logout()

    def __initializeEventManager(self):
        # init event manager and all events
        self.__eventManager = EventManager()
        allEvents = inspect.getmembers(AllEvents, inspect.isclass)

        for _, cls in allEvents:
            self.__eventManager.registerEvent(cls)

    def __initializeSystems(self):
        self.__movementSystem = TankMovementSystem(self.__map, self.__eventManager, self.__pathingOffsets)
        self.__shootingSystem = TankShootingSystem(self.__map, self.__eventManager, self.__pathingOffsets,
                                                   self.__gameState["attack_matrix"],
                                                   self.__gameState["catapult_usage"])
        self.__healthSystem = TankHealthSystem(self.__eventManager)
        self.__respawnSystem = TankRespawnSystem(self.__eventManager)
        self.__positionBonusSystem = PositionBonusSystem(self.__map, self.__eventManager)

    def __initializeDisplay(self):
        self.__displaySystem = DisplaySystem(self.__map, self.__eventManager)

    def __initializeTurnOrder(self):
        turnOrder = ["spg", "light_tank", "heavy_tank", "medium_tank", "at_spg"]

        self.__playerTanks = [None] * 5
        for tankId, tankData in self.__gameState["vehicles"].items():
            if tankData["player_id"] == self.__playerID:
                self.__playerTanks[turnOrder.index(tankData["vehicle_type"])] = tankId

    def __initializeWorld(self):
        self.__gameState = self.__session.getGameState()
        self.__initializeEventManager()
        self.__tankManager = TankManager(self.__eventManager)
        self.__initializeSystems()
        self.__initializeDisplay()
        self.__initializeTurnOrder()

    def __resetWorld(self):
        self.__previousPlayer = "Unknown"
        self.__gameState = self.__session.getGameState()
        self.__initializeEventManager()
        self.__tankManager = TankManager(self.__eventManager)
        self.__initializeSystems()
        self.__displaySystem.reset(self.__eventManager)
        self.__initializeTurnOrder()

    def __addMissingTanks(self):
        for tankId, tankData in self.__gameState["vehicles"].items():
            tankId = str(tankId)
            if not self.__tankManager.hasTank(tankId):
                self.__tankManager.addTank(tankId, tankData)

    def __turn(self, currentPlayer: int):
        self.__respawnSystem.turn()
        self.__positionBonusSystem.turn()
        self.__displaySystem.turn()
        self.__shootingSystem.turn(currentPlayer)

    def __selfTurn(self):
        for tankId in self.__playerTanks:
            # perform local player actions
            try:
                options = self.__shootingSystem.getShootingOptions(tankId)
                if len(options) > 0:
                    randomChoice = random.randint(0, len(options) - 1)
                    self.__session.shoot({"vehicle_id": int(tankId), "target": TupleToHex(options[randomChoice][0])})
                    self.__shootingSystem.shoot(tankId, options[randomChoice][0])
                    continue

                options = self.__movementSystem.getMovementOptions(tankId)
                if len(options) > 0:
                    bestOptions = self.__bot.getBestMove(options)
                    randomChoice = random.randint(0, len(bestOptions) - 1)
                    self.__session.move({"vehicle_id": int(tankId), "target": TupleToHex(bestOptions[randomChoice])})
                    self.__movementSystem.move(tankId, bestOptions[randomChoice])
            except BadCommandException as exception:
                logging.debug(f"BadCommandException:{exception.message}")
                if exception.message != "You have already used this vehicle!":
                    self.__resetWorld()
                    return

        self.__session.nextTurn()

    def __otherTurn(self):
        # skip turn since it's not our
        self.__session.nextTurn()
        # add missing tanks
        self.__addMissingTanks()
        # perform other player actions
        gameActions = self.__session.getGameActions()

        for action in gameActions["actions"]:
            if action["player_id"] == self.__playerID:
                break
            if action["action_type"] == Action.MOVE:
                actionData = action["data"]
                self.__movementSystem.move(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))
            elif action["action_type"] == Action.SHOOT:
                actionData = action["data"]
                self.__shootingSystem.shoot(str(actionData["vehicle_id"]), HexToTuple(actionData["target"]))

    def __play(self):
        self.__previousPlayer = "Unknown"

        while not self.__gameState["finished"]:
            try:
                self.__addMissingTanks()
                currentPlayer = self.__gameState["current_player_idx"]
                if currentPlayer and currentPlayer != self.__previousPlayer:
                    self.__previousPlayer = currentPlayer
                    self.__turn(currentPlayer)

                    if currentPlayer == self.__playerID:  # our turn
                        self.__selfTurn()
                    else:
                        self.__otherTurn()
                else:
                    self.__session.nextTurn()
                self.__gameState = self.__session.getGameState()
            except TimeoutException as exception:
                logging.debug(f"TimeoutException:{exception.message}")
                self.__gameState = self.__session.getGameState()
            except (InappropriateGameStateException, InternalServerErrorException) as exception:
                logging.debug(f"{exception.__class__.__name__}:{exception.message}")
                self.__resetWorld()

    def quitDisplay(self):
        self.__displaySystem.stop()

    def isWinner(self) -> bool:
        return self.__playerID == self.__gameState["winner"]


class InputException(Exception):
    def __init__(self, message):
        self.message = message
        Exception.__init__(self)


def play():
    print("Name: ", end="")
    name = input()

    if not name:
        print("Invalid name!")
        return

    print("Password (leave empty to skip): ", end="")
    password = input()

    with PlayerSession(name, password) as session:
        data = {}
        while True:
            try:
                data.clear()

                print("Joining or creating a game? (J/C): ", end="")
                playType = input()

                if not (playType.upper() == "C" or playType.upper() == "J"):
                    raise InputException("Invalid input!")

                print("Enter game name: ", end="")
                gameName = input()
                if not gameName:
                    raise InputException("Invalid game name!")
                data["game"] = gameName

                if playType.upper() == "C":
                    print("Enter turn count (max - 100): ", end="")
                    turnCount = int(input())
                    if 0 < turnCount < 101:
                        data["num_turns"] = turnCount
                    else:
                        raise InputException("Invalid turn count!")

                    print("Enter player count (1-3): ", end="")
                    playerCount = int(input())
                    if 0 < playerCount < 4:
                        data["num_players"] = playerCount
                    else:
                        raise InputException("Invalid player count!")

                print("Are you an observer? (Y/N): ", end="")
                isObserver = input()
                if isObserver.upper() == "Y":
                    data["is_observer"] = True
                elif not isObserver.upper() == "N":
                    raise InputException("Invalid input!")

                print("Playing...")
                try:
                    game = Game(session, data)

                    if not isObserver.upper() == "Y":
                        if game.isWinner():
                            print("You win!")
                        else:
                            print("You lose!")
                    else:
                        print("Game ended!")
                except AccessDeniedException as exception:
                    print(f"AccessDeniedException:{exception.message}")
                    break

                print("Play again? (Y/Any): ", end="")
                playAgain = input()
                game.quitDisplay()
                if not playAgain.upper() == "Y":
                    return
            except InputException as e:
                print(e.message)
            except ValueError:
                print("Invalid input!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR)

    play()
