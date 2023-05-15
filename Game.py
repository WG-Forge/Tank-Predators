from Exceptions import BadCommandException, InappropriateGameStateException, TimeoutException, \
    InternalServerErrorException
from PlayerSession import PlayerSession
from Utils import hexToTuple
from Utils import tupleToHex
from ServerConnection import Action
import logging
from Aliases import jsonDict
from World import World


class Game:
    def __init__(self, session: PlayerSession, data: jsonDict) -> None:
        self.__session = session
        self.__playerID = self.__session.login(data)

        # Get static map data
        self.__map = self.__session.getMapInfo()
        self.__gameState = self.__session.getGameState()
        self.__world = World(self.__map, self.__gameState)
        self.__player = self.__world.getEntityManagementSystem().getPlayer(self.__playerID)
        self.__previousPlayer = None
        self.__turn()
        self.__bot = self.__world.getBot()
        self.__bot.currentUser(self.__playerID)
        self.__run()
        self.__session.logout()

    def __reset(self):
        self.__previousPlayer = None
        self.__gameState = self.__session.getGameState()
        self.__world.resetSystems(self.__gameState)
        self.__turn()
        self.__player = self.__world.getEntityManagementSystem().getPlayer(self.__playerID)

    def __selfTurn(self):
        actions = self.__bot.getActions()
        
        for action in actions:
            if action[0] == "shoot":
                self.__session.shoot({"vehicle_id": int(action[1]), "target": tupleToHex(action[2])})
                self.__world.shoot(action[1], action[2])
            elif action[0] == "move":
                self.__session.move({"vehicle_id": int(action[1]), "target": tupleToHex(action[2])})
                self.__world.move(action[1], action[2])

        self.__session.nextTurn()

    def __otherTurn(self):
        # skip turn since it's not our
        self.__session.nextTurn()
        # perform other player actions
        gameActions = self.__session.getGameActions()

        for action in gameActions["actions"]:
            if self.__player is not None and action["player_id"] == self.__player.getId():
                break
            if action["action_type"] == Action.MOVE:
                actionData = action["data"]
                self.__world.move(str(actionData["vehicle_id"]), hexToTuple(actionData["target"]))
            elif action["action_type"] == Action.SHOOT:
                actionData = action["data"]
                self.__world.shoot(str(actionData["vehicle_id"]), hexToTuple(actionData["target"]))

    def __turn(self) -> None:
        self.__world.addMissingTanks(self.__gameState)
        self.__world.addMissingPlayers(self.__gameState)
        self.__world.turn(self.__gameState)

    def __round(self) -> None:
        if self.__gameState["current_turn"] % self.__gameState["num_players"] == 0:
            self.__world.round()

    def __run(self):
        while True:
            self.__play()
            if self.__gameState["current_round"] != self.__gameState["num_rounds"]:
                self.__session.nextTurn()
                self.__reset()
            else:
                logging.debug(self.__gameState)
                return

    def __play(self):
        while not self.__gameState["finished"]:
            try:
                currentPlayer = self.__gameState["current_player_idx"]
                if currentPlayer != self.__previousPlayer:
                    self.__previousPlayer = currentPlayer

                    if self.__player is not None and currentPlayer == self.__player.getId():  # our turn
                        self.__selfTurn()
                    else:
                        self.__otherTurn()
                else:
                    self.__session.nextTurn()

                self.__gameState = self.__session.getGameState()
                self.__turn()
                self.__round()
            except TimeoutException as exception:
                logging.debug(f"TimeoutException:{exception.message}")
            except (InappropriateGameStateException, InternalServerErrorException) as exception:
                logging.debug(f"{exception.__class__.__name__}:{exception.message}")
                self.__reset()
            except BadCommandException as exception:
                logging.debug(f"BadCommandException:{exception.message}")
                self.__session.nextTurn()
                self.__reset()
        print("playerID: " + str(self.__player.getId()))
        #for player in self.__world.getEntityManagementSystem().getPlayers().values():
        #    print("ID:" + str(player.getId()) + ", capturePoints:" + str(player.getCapturePoints()) + ", destructionPoints:" + str(player.getDestructionPoints()))
        print("winner: ", self.__gameState["winner"])
        print(self.__gameState["win_points"])
        print("------------------------------------")


    def quit(self):
        self.__world.quit()

    def isWinner(self) -> bool:
        return self.__player.getId() == self.__gameState["winner"]
